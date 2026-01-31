#!/usr/bin/env python3
"""Add a RabbitMQ user with MQTT and app queue permissions.

By default grants permissions on vhosts / and home. User 'user' and 'guest'
only get access to vhost /, not home.
"""

import argparse
import subprocess
import sys


def run(cmd: list[str], check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a command; use sudo for rabbitmqctl."""
    full = ["sudo", "rabbitmqctl"] + cmd
    return subprocess.run(
        full, check=check, capture_output=capture, text=True
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add RabbitMQ user with IOT/MQTT tags and permissions on vhosts / and home."
    )
    parser.add_argument("username", help="RabbitMQ username")
    parser.add_argument("password", help="RabbitMQ password")
    args = parser.parse_args()

    user = args.username
    password = args.password

    # user and guest: only vhost /, and only the "user" tag
    restricted = user in ("user", "guest")
    home_vhost = None if restricted else "home"
    tags = ["user"] if restricted else ["IOT", "users", "MQTT"]

    try:
        # Add user, or update password if user already exists
        result = run(["add_user", user, password], check=False, capture=True)
        if result.returncode != 0:
            if "already exists" in (result.stderr or "").lower():
                run(["change_password", user, password])
            else:
                print(result.stderr or result.stdout or f"Exit {result.returncode}", file=sys.stderr)
                return result.returncode

        run(["set_user_tags", user] + tags)
        # vhost '/': MQTT plugin creates mqtt-subscription-<client_id> queues here
        run(
            [
                "set_permissions",
                "-p",
                "/",
                user,
                f"(^mqtt-subscription-.*|^{user}-.*)",
                ".*",
                ".*",
            ]
        )
        # vhost 'home': app queues (not for user/guest)
        if home_vhost:
            run(["set_permissions", "-p", home_vhost, user, f"^{user}-.*", ".*", ".*"])
    except subprocess.CalledProcessError as e:
        print(f"Error: rabbitmqctl failed with exit code {e.returncode}", file=sys.stderr)
        return e.returncode

    vhosts = "/ and home" if home_vhost else "/ only"
    print(f"User '{user}' added/updated with permissions on vhost(s) {vhosts}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
