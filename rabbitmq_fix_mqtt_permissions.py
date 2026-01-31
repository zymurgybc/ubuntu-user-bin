#!/usr/bin/env python3
"""Fix RabbitMQ MQTT permissions in vhost / for all users.

Addresses "configure access to queue 'mqtt-subscription-...' refused" errors.
The MQTT plugin creates queues named mqtt-subscription-<client_id> in vhost '/'.

Reads all users from RabbitMQ and sets MQTT permissions on vhost / for each.
Policy: 'user' and 'guest' accounts only get access to vhost /, not home.
"""

import argparse
import re
import subprocess
import sys


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
    # Output: "Listing users ..." then "user\t[tags]" lines, or table header "user  configure  write  read"
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith("Listing"):
            continue
        parts = line.split()
        if not parts:
            continue
        name = parts[0]
        if name == "Listing":
            continue
        # Skip permissions table header: "user    configure   write   read"
        if len(parts) >= 2 and name == "user" and parts[1] == "configure":
            continue
        users.add(name)
    return users


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fix MQTT permissions in vhost / for all RabbitMQ users."
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
    users = sorted(list_users())
    if not users:
        print("No RabbitMQ users found.", file=sys.stderr)
        return 1

    print(f"Setting MQTT permissions in vhost '{vhost}' for all users: {users}")
    print("  (user and guest get / only, not home)")
    print()

    for user in users:
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
            stderr = (e.stderr or "").strip()
            # Only skip when RabbitMQ explicitly says this user does not exist
            # (e.g. "User 'user' does not exist"), not other "does not exist" errors
            user_gone = re.search(
                r"User\s+['\"]?" + re.escape(user) + r"['\"]?\s+does not exist",
                stderr,
                re.IGNORECASE,
            )
            if user_gone:
                print(f"  SKIP: {user} (no longer exists)")
                continue
            print(f"  FAIL: {user} - {stderr or e}", file=sys.stderr)
            return e.returncode

    print()
    print(f"Done. Check with: sudo rabbitmqctl list_permissions -p {vhost}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
