"""Generate a one-time bootstrap capability on the host, never a default password."""

import argparse
import os
from pathlib import Path

from sqlalchemy.orm import Session

from infra.admin_security import AdminSecurity
from infra.db import make_engine
from infra.settings import Settings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(".local/admin-bootstrap.token"))
    args = parser.parse_args()
    config = Settings()
    engine = make_engine(config.database_url)
    with Session(engine) as session:
        token = AdminSecurity(session, config).bootstrap_token()
    path = args.output
    path.parent.mkdir(exist_ok=True, parents=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write(token + "\n")
    engine.dispose()
    print(f"一次性初始化凭证已写入 {path}（0600，15分钟有效）。")
    print("打开 http://127.0.0.1:3100/admin/login，选择初始化管理员；请勿分享该文件。")


if __name__ == "__main__":
    main()
