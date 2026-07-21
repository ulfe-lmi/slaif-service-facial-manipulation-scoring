#!/usr/bin/python3
"""Stage a bind-mounted secret, drop privileges, and start the service."""

from __future__ import annotations

import os
import pwd
import shutil
import stat
import sys
import tempfile
from pathlib import Path

SERVICE_USER = "slaif"
API_KEY_ENV = "SLAIF_FMS_API_KEY_FILE"
PRIVATE_SECRET_DIR = Path("/run/slaif-fms")


def stage_api_key(user: pwd.struct_passwd) -> None:
    """Copy a root-readable host secret for the non-root service process."""
    configured = os.environ.get(API_KEY_ENV)
    if not configured:
        return

    source = Path(configured)
    try:
        source_stat = source.stat()
    except FileNotFoundError:
        return

    if not stat.S_ISREG(source_stat.st_mode):
        return

    PRIVATE_SECRET_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    PRIVATE_SECRET_DIR.chmod(0o700)
    os.chown(PRIVATE_SECRET_DIR, user.pw_uid, user.pw_gid)

    descriptor, temporary_name = tempfile.mkstemp(dir=PRIVATE_SECRET_DIR, prefix=".api_key.")
    temporary = Path(temporary_name)
    destination = PRIVATE_SECRET_DIR / "api_key"
    try:
        with os.fdopen(descriptor, "wb") as output, source.open("rb") as input_file:
            shutil.copyfileobj(input_file, output)
            output.flush()
            os.fsync(output.fileno())
        temporary.chmod(0o600)
        os.chown(temporary, user.pw_uid, user.pw_gid)
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)

    os.environ[API_KEY_ENV] = str(destination)


def drop_privileges(user: pwd.struct_passwd) -> None:
    os.initgroups(user.pw_name, user.pw_gid)
    os.setgid(user.pw_gid)
    os.setuid(user.pw_uid)


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("No service command was provided.")

    if os.geteuid() == 0:
        service_user = pwd.getpwnam(SERVICE_USER)
        stage_api_key(service_user)
        drop_privileges(service_user)

    os.execvp(sys.argv[1], sys.argv[1:])


if __name__ == "__main__":
    main()
