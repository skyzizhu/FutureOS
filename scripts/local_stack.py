"""Run native API, Worker, Web and a local Redis; use configured PostgreSQL.

uv run --group local python -m scripts.local_stack [--verify]
Build Web first. Ctrl-C stops only services started by this supervisor.
"""

import argparse
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx
import redis
from dotenv import dotenv_values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--stop", action="store_true")
    args = parser.parse_args()
    marker = Path(".local/stack.pid")
    if args.stop:
        if not marker.exists():
            print("No managed FutureOS stack is running")
            return
        pid = int(marker.read_text())
        command = subprocess.run(
            ["ps", "-p", str(pid), "-o", "command="], capture_output=True, text=True
        ).stdout
        if "scripts.local_stack" not in command:
            marker.unlink(missing_ok=True)
            raise SystemExit("Stale PID marker removed; no process was stopped")
        os.kill(pid, signal.SIGTERM)
        print("Stopping managed FutureOS stack")
        return
    file_env = {key: value for key, value in dotenv_values(".env").items() if value is not None}
    env = {**os.environ, **file_env, "DEMO_MODE": "true", "NEXT_TELEMETRY_DISABLED": "1"}
    api_port = int(env.get("FUTUREOS_API_PORT", "8100"))
    web_port = int(env.get("FUTUREOS_WEB_PORT", "3100"))
    for port in (api_port, web_port):
        with socket.socket() as probe:
            if probe.connect_ex(("127.0.0.1", port)) == 0:
                raise SystemExit(
                    f"Port {port} already in use; choose another FutureOS port in .env"
                )
    folder = Path(".local").resolve()
    folder.mkdir(exist_ok=True)
    redis_url = env.get("REDIS_URL", "redis://127.0.0.1:6381/0")
    env.update(
        REDIS_URL=redis_url,
        REQUIRE_REDIS="true",
        PORT=str(web_port),
        FUTUREOS_API_PORT=str(api_port),
        FUTUREOS_WEB_PORT=str(web_port),
        API_INTERNAL_URL=f"http://127.0.0.1:{api_port}",
        BROWSER_TEST_URL=f"http://127.0.0.1:{web_port}",
    )
    if args.verify:
        env["DEMO_ADMIN_ENABLED"] = "true"
        # Acceptance must never use live email or CAPTCHA credentials from .env.
        env["AUTH_MAIL_TRANSPORT"] = "local_preview"
        env["TURNSTILE_ENABLED"] = "false"
        env["LIVE_WEB_ENABLED"] = "false"
        env["LIVE_RESEARCH_ENABLED"] = "false"
        env["LIVE_CHAT_ENABLED"] = "false"
        env["LIVE_EMAIL_ENABLED"] = "false"
        env["LIVE_PAYMENTS_ENABLED"] = "false"
        env["SANDBOX_COMMERCE_ENABLED"] = "true"
        # Empty environment values also override dotenv fallback inside Settings.
        env.update(
            SMTP_HOST="",
            SMTP_PORT="587",
            SMTP_USERNAME="",
            SMTP_PASSWORD="",
            SMTP_FROM="futureos@example.invalid",
            TURNSTILE_SITE_KEY="",
            TURNSTILE_SECRET_KEY="",
            DEEPSEEK_API_KEY="",
        )
    postgres_server = None
    if env.get("FUTUREOS_MANAGED_POSTGRES") == "true":
        import pgserver

        postgres_server = pgserver.get_server(folder / "postgres-demo", cleanup_mode="stop")
    marker.write_text(str(os.getpid()))
    children = []
    logs = []
    managed_redis = None

    def run(command: list[str]) -> None:
        subprocess.run(command, env=env, check=True)

    def spawn(name: str, command: list[str]) -> None:
        log = (folder / f"{name}.log").open("wb")
        logs.append(log)
        child_env = dict(env)
        if name == "web":
            for secret_name in (
                "DEEPSEEK_API_KEY",
                "TURNSTILE_SECRET_KEY",
                "DATABASE_URL",
                "TEST_DATABASE_URL",
                "DEMO_ADMIN_TOKEN",
                "SMTP_PASSWORD",
                "BOUNCE_WEBHOOK_SECRET",
            ):
                child_env.pop(secret_name, None)
        children.append(
            subprocess.Popen(
                command, env=child_env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True
            )
        )

    def stop(_signum, _frame) -> None:
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop)
    try:
        probe = redis.Redis.from_url(redis_url, socket_connect_timeout=0.5, socket_timeout=0.5)
        try:
            probe.ping()
            print("Reusing running local Redis", flush=True)
        except redis.RedisError:
            endpoint = urlparse(redis_url)
            if endpoint.hostname not in {"127.0.0.1", "localhost"}:
                raise RuntimeError(
                    "Start remote Redis separately; supervisor starts local Redis only"
                ) from None
            redis_binary = shutil.which("redis-server")
            if redis_binary:
                spawn(
                    "redis",
                    [
                        redis_binary,
                        "--bind",
                        "127.0.0.1",
                        "--port",
                        str(endpoint.port or 6381),
                        "--dir",
                        str(folder),
                        "--dbfilename",
                        "redis-demo.rdb",
                    ],
                )
            else:
                import redislite

                managed_redis = redislite.Redis(
                    str(folder / "redis-demo.rdb"),
                    serverconfig={"port": str(endpoint.port or 6381), "bind": "127.0.0.1"},
                )
                assert managed_redis.ping()
                print("Started installed project-local Redis server", flush=True)
            for _ in range(30):
                try:
                    if probe.ping():
                        break
                except redis.RedisError:
                    time.sleep(0.1)
            else:
                raise RuntimeError("Redis did not start")
        if args.verify:
            if not env.get("TEST_DATABASE_URL"):
                raise RuntimeError("--verify requires a separate TEST_DATABASE_URL ending in _test")
            run([sys.executable, "-m", "pytest", "-q"])
            # Browser security tests must not fill live login budgets or provision
            # administrators in the user's development database.
            env["DATABASE_URL"] = env["TEST_DATABASE_URL"]
            env["APP_ENV"] = "test"
            env["PROFILE_KEY_PATH"] = str(folder / "e2e" / "private-profile.key")
            run([sys.executable, "-m", "scripts.reset_e2e_database"])
        run([sys.executable, "-m", "alembic", "upgrade", "head"])
        run([sys.executable, "-m", "scripts.seed_demo"])
        spawn(
            "api",
            [
                sys.executable,
                "-m",
                "uvicorn",
                "apps.api.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(api_port),
                "--no-access-log",
                "--no-proxy-headers",
                "--log-config",
                "infra/logging.json",
            ],
        )
        spawn("worker", [sys.executable, "-m", "workers.research.main"])
        spawn("scheduler", [sys.executable, "-m", "workers.scheduler.main"])
        spawn(
            "web",
            [
                "npm",
                "run",
                "start",
                "--workspace",
                "@futureos/web",
                "--",
                "--port",
                str(web_port),
                "--hostname",
                "127.0.0.1",
            ],
        )
        for _ in range(60):
            if any(child.poll() is not None for child in children):
                raise RuntimeError("A service exited; inspect .local/{api,worker,web}.log")
            try:
                if (
                    httpx.get(
                        f"http://127.0.0.1:{api_port}/api/v1/health/ready", trust_env=False
                    ).status_code
                    == 200
                    and httpx.get(f"http://127.0.0.1:{web_port}", trust_env=False).status_code
                    == 200
                ):
                    break
            except httpx.HTTPError:
                pass
            time.sleep(0.5)
        else:
            raise RuntimeError("Local stack readiness timed out")
        print(
            f"DEMO PostgreSQL + Redis + API + Worker + Web ready at http://127.0.0.1:{web_port}",
            flush=True,
        )
        run([sys.executable, "-m", "scripts.smoke"])
        if args.verify:
            run([sys.executable, "-m", "workers.research.main", "--heartbeat"])
            run(["npm", "run", "e2e"])
            return
        while all(child.poll() is None for child in children):
            time.sleep(1)
        raise RuntimeError("A service exited; inspect .local logs")
    except KeyboardInterrupt:
        pass
    finally:
        for child in children:
            os.killpg(child.pid, signal.SIGTERM)
        for child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
        for log in logs:
            log.close()
        if managed_redis is not None:
            managed_redis.shutdown()
        if postgres_server is not None:
            postgres_server.cleanup()
        if marker.exists() and marker.read_text() == str(os.getpid()):
            marker.unlink()


if __name__ == "__main__":
    main()
