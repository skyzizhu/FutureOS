"""Authenticated local backups and isolated PostgreSQL restore drills; never restore in place."""

import io
import json
import os
import subprocess
import sys
import time
import zipfile
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy import inspect, select, text
from sqlalchemy.engine import Connection, make_url
from sqlalchemy.orm import Session

from infra.db import UserReportVersion, make_engine
from infra.erasure_journal import read_tombstones
from infra.personal_data import apply_erasure
from infra.privacy import PrivacyVault
from infra.reports import ReportRepository
from infra.settings import Settings

MAGIC = b"FutureOSBackupV1\x00"
AAD = b"futureos-native-backup-v1"


def encrypt_bundle(payload: bytes, key: bytes) -> bytes:
    nonce = os.urandom(12)
    return MAGIC + nonce + AESGCM(key).encrypt(nonce, payload, AAD)


def decrypt_bundle(bundle: bytes, key: bytes) -> dict[str, bytes]:
    if not bundle.startswith(MAGIC) or len(bundle) > 256_000_000:
        raise ValueError("BACKUP_FORMAT_INVALID")
    data = AESGCM(key).decrypt(bundle[len(MAGIC) : len(MAGIC) + 12], bundle[len(MAGIC) + 12 :], AAD)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if sorted(archive.namelist()) != ["db.dump", "manifest.json", "private-profile.key"]:
            raise ValueError("BACKUP_MEMBERS_INVALID")
        if any(info.file_size > 256_000_000 for info in archive.infolist()):
            raise ValueError("BACKUP_TOO_LARGE")
        files = {name: archive.read(name) for name in archive.namelist()}
    manifest = json.loads(files["manifest.json"])
    if (
        sha256(files["db.dump"]).hexdigest() != manifest["dump_sha256"]
        or len(files["private-profile.key"]) != 32
    ):
        raise ValueError("BACKUP_INTEGRITY_INVALID")
    return files


def pg_env(database_url: str) -> dict[str, str]:
    url = make_url(database_url)
    if url.get_backend_name() != "postgresql":
        raise ValueError("POSTGRESQL_REQUIRED")
    host = str(url.query.get("host", url.host or ""))
    if host not in {"localhost", "127.0.0.1", "::1"} and not host.startswith(
        str(Path(".local/postgres-demo").resolve())
    ):
        raise ValueError("PROJECT_LOCAL_POSTGRES_REQUIRED")
    return {
        "PATH": os.environ.get("PATH", ""),
        "PGUSER": url.username or "",
        "PGPASSWORD": url.password or "",
        "PGDATABASE": url.database or "",
        "PGHOST": host,
        "PGPORT": str(url.port or 5432),
        "PGCONNECT_TIMEOUT": "5",
    }


def fingerprint(connection: Connection) -> dict[str, Any]:
    names = sorted(inspect(connection).get_table_names())
    counts = {
        name: connection.exec_driver_sql('SELECT count(*) FROM "' + name + '"').scalar_one()
        for name in names
    }
    private = connection.exec_driver_sql(
        "SELECT id,ciphertext,immutable_hash FROM user_report_versions ORDER BY id"
    ).all()
    public = connection.exec_driver_sql(
        "SELECT id,immutable_hash FROM forecast_versions ORDER BY id"
    ).all()
    auth = {}
    for table, key in [
        ("auth_accounts", "user_id"),
        ("auth_sessions", "token_hash"),
        ("admin_mfa", "user_id"),
        ("admin_access", "user_id"),
        ("auth_challenges", "token_hash"),
        ("auth_email_codes", "id"),
    ]:
        if table in names:
            auth[table] = [
                tuple(map(str, row))
                for row in connection.exec_driver_sql(
                    f'SELECT * FROM "{table}" ORDER BY "{key}"'
                ).all()
            ]
    return {
        "counts": counts,
        "authentication_digest": sha256(json.dumps(auth, sort_keys=True).encode()).hexdigest(),
        "private_digest": sha256(
            json.dumps([tuple(map(str, r)) for r in private]).encode()
        ).hexdigest(),
        "public_digest": sha256(
            json.dumps([tuple(map(str, r)) for r in public]).encode()
        ).hexdigest(),
    }


def create_backup(
    config: Settings,
    folder: Path = Path(".local/backups"),
    transport_key: Path = Path(".local/backup-transport.key"),
) -> Path:
    from pgserver._commands import POSTGRES_BIN_PATH

    folder.mkdir(parents=True, exist_ok=True)
    if transport_key.resolve() == Path(config.profile_key_path).resolve():
        raise ValueError("BACKUP_KEY_MUST_BE_SEPARATE")
    key = PrivacyVault(str(transport_key), create=True).key
    profile_key = PrivacyVault(config.profile_key_path).key
    engine = make_engine(config.database_url)
    with engine.connect().execution_options(isolation_level="REPEATABLE READ") as connection:
        snapshot = connection.scalar(text("SELECT pg_export_snapshot()"))
        stamp = fingerprint(connection)
        result = subprocess.run(
            [
                str(POSTGRES_BIN_PATH / "pg_dump"),
                "--format=custom",
                "--no-owner",
                "--no-acl",
                "--snapshot=" + str(snapshot),
            ],
            env=pg_env(config.database_url),
            capture_output=True,
            check=True,
            timeout=120,
        )
        manifest = {
            "created_at": datetime.now().astimezone().isoformat(),
            "dump_sha256": sha256(result.stdout).hexdigest(),
            "database_fingerprint": stamp,
            "migration_head": connection.scalar(text("SELECT version_num FROM alembic_version")),
        }
    engine.dispose()
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("db.dump", result.stdout)
        archive.writestr("private-profile.key", profile_key)
        archive.writestr("manifest.json", json.dumps(manifest))
    blob = encrypt_bundle(output.getvalue(), key)
    decrypt_bundle(blob, key)
    destination = folder / ("futureos_" + uuid4().hex + ".fosbackup")
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(blob)
        stream.flush()
        os.fsync(stream.fileno())
    return destination


def restore_drill(
    config: Settings, backup: Path, transport_key: Path = Path(".local/backup-transport.key")
) -> dict[str, Any]:
    import tempfile

    import psycopg.sql
    from pgserver._commands import POSTGRES_BIN_PATH
    from pgserver.postgres_server import get_server

    files = decrypt_bundle(backup.read_bytes(), PrivacyVault(str(transport_key)).key)
    manifest = json.loads(files["manifest.json"])
    tombstones = read_tombstones(config.profile_key_path)
    server = get_server(Path(".local/postgres-demo").resolve(), cleanup_mode=None)
    admin = make_engine(
        make_url(server.get_uri())
        .set(drivername="postgresql+psycopg")
        .render_as_string(hide_password=False)
    ).execution_options(isolation_level="AUTOCOMMIT")
    source = make_url(config.database_url)
    target = "futureos_m7_" + uuid4().hex[:16] + "_restore_drill"
    target_url = source.set(database=target).render_as_string(hide_password=False)
    started = time.monotonic()
    target_engine = None
    created = False
    try:
        with admin.connect() as connection:
            raw = connection.connection.driver_connection
            assert raw is not None
            raw.execute(
                psycopg.sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    psycopg.sql.Identifier(target),
                    psycopg.sql.Identifier(source.username or "futureos_local"),
                )
            )
        created = True
        subprocess.run(
            [
                str(POSTGRES_BIN_PATH / "pg_restore"),
                "--no-owner",
                "--no-acl",
                "--exit-on-error",
                "--dbname=" + target,
            ],
            input=files["db.dump"],
            env=pg_env(target_url),
            capture_output=True,
            check=True,
            timeout=120,
        )
        target_engine = make_engine(target_url)
        with target_engine.connect() as connection:
            restored = fingerprint(connection)
        expected = manifest["database_fingerprint"]
        if {key: restored.get(key) for key in expected} != expected:
            raise ValueError("RESTORE_FINGERPRINT_MISMATCH")
        verified = 0
        verified_accounts = 0
        verified_factors = 0
        with tempfile.TemporaryDirectory(prefix="futureos-restore-key-") as temporary:
            path = Path(temporary) / "profile.key"
            path.write_bytes(files["private-profile.key"])
            path.chmod(0o600)
            restored_config = config.model_copy(
                update={"database_url": target_url, "profile_key_path": str(path)}
            )
            # First validate the original snapshot, then migrate only the isolated
            # clone so current erasure replay also works for pre-security backups.
            subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                env={
                    **os.environ,
                    "DATABASE_URL": target_url,
                    "APP_ENV": "test",
                    "PROFILE_KEY_PATH": str(path),
                },
                capture_output=True,
                check=True,
                timeout=120,
            )
            with target_engine.connect() as connection:
                target_head = connection.scalar(text("SELECT version_num FROM alembic_version"))
            with Session(target_engine) as session:
                for version in session.scalars(select(UserReportVersion).limit(50)):
                    ReportRepository(session, restored_config).report(
                        version.user_id, version.report_id, version.id
                    )
                    verified += 1
                vault = PrivacyVault(str(path))
                for uid, ciphertext in session.execute(
                    text("SELECT user_id,email_ciphertext FROM auth_accounts")
                ):
                    vault.open(ciphertext, "account:" + str(uid))
                    verified_accounts += 1
                if "admin_mfa" in restored["counts"]:
                    import pyotp

                    for uid, ciphertext in session.execute(
                        text("SELECT user_id,secret_ciphertext FROM admin_mfa")
                    ):
                        secret = vault.open(ciphertext, "admin-mfa:" + str(uid))["secret"]
                        assert len(pyotp.TOTP(secret).now()) == 6
                        verified_factors += 1
            applied = 0
            from infra.db import AuthAccount

            for tombstone in tombstones:
                with Session(target_engine) as session:
                    uid = UUID(tombstone["user_id"])
                    if session.get(AuthAccount, uid) is not None:
                        apply_erasure(
                            session,
                            uid,
                            restored_config,
                            UUID(tombstone["erasure_id"]),
                            datetime.fromisoformat(tombstone["erased_at"]),
                        )
                        applied += 1
        report = {
            "passed": True,
            "backup_created_at": manifest["created_at"],
            "backup_migration_head": manifest["migration_head"],
            "restored_target_migration_head": target_head,
            "table_count": len(restored["counts"]),
            "private_reports_decrypted": verified,
            "account_emails_decrypted": verified_accounts,
            "admin_mfa_secrets_verified": verified_factors,
            "authentication_fingerprint_verified": "authentication_digest" in expected,
            "snapshot_fingerprint_identical": True,
            "tombstones_checked": len(tombstones),
            "deletions_replayed": applied,
            "restore_seconds": round(time.monotonic() - started, 3),
            "isolated_database_removed": True,
            "limits": [
                "本机单次演练，不是RTO/RPO服务承诺",
                "恢复前还需核对备份之后的计费变化；未开启真实支付",
            ],
        }
        return report
    finally:
        if target_engine:
            target_engine.dispose()
        if created:
            assert target.endswith("_restore_drill") and target != source.database
            with admin.connect() as connection:
                raw = connection.connection.driver_connection
                assert raw is not None
                raw.execute(
                    psycopg.sql.SQL("DROP DATABASE {} WITH (FORCE)").format(
                        psycopg.sql.Identifier(target)
                    )
                )
        admin.dispose()
