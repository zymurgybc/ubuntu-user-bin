#!/usr/bin/env python3
"""Fix RabbitMQ MQTT permissions in vhost /.

Addresses "configure access to queue 'mqtt-subscription-...' refused" errors.
The MQTT plugin creates queues named mqtt-subscription-<client_id> in vhost '/'.

Policy: 'user' and 'guest' accounts only get access to vhost /, not home.
This script only sets permissions on vhost / (no home).
"""

import argparse
import subprocess
import sys


DEFAULT_MQTT_USERS = ["homeassistant", "linknlink"]
VHOST_ONLY_SLASH = ("user", "guest")  # These accounts get / only, not home


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command; use sudo for rabbitmqctl."""
    full = ["sudo", "rabbitmqctl"] + cmd
    return subprocess.run(full, check=check, capture_output=True, text=True)


def list_users() -> set[str]:
    """Return set of existing RabbitMQ usernames."""
    result = subprocess.run(
        ["sudo", "rabbitmqctl", "list_users"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return set()
    users = set()
    # Format: user\t[tags]\n
    for line in result.stdout.splitlines():
        if line.strip():
            users.add(line.split()[0])
    return users


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fix MQTT permissions in vhost / for listed users (user/guest get / only, not home)."
    )
    parser.add_argument(
        "users",
        nargs="*",
        default=DEFAULT_MQTT_USERS,
        help=f"Usernames to fix (default: {DEFAULT_MQTT_USERS})",
    )
    parser.add_argument(
        "-p",
        "--vhost",
        default="/",
        metavar="VHOST",
        help="Vhost to set permissions in (default: /)",
    )
    args = parser.parse_args()

    vhost = args.vhost
    existing = list_users()

    print(f"Setting MQTT permissions in vhost '{vhost}' for: {args.users}")
    print("  (user and guest get / only, not home)")
    print()

    for user in args.users:
        if user not in existing:
            print(f"  SKIP: {user} (user not found)")
            continue
        try:
            # Configure: mqtt-subscription-* and <username>-*
            run(
                [
                    "set_permissions",
                    "-p",
                    vhost,
                    user,
                    f"(^mqtt-subscription-.*|^{user}-.*)",
                    ".*",
                    ".*",
                ]
            )
            print(f"  OK: {user}")
        except subprocess.CalledProcessError as e:
            print(f"  FAIL: {user} - {e.stderr or e}", file=sys.stderr)
            return e.returncode

    print()
    print(f"Done. Check with: sudo rabbitmqctl list_permissions -p {vhost}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
