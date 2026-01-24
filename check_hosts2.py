#!/usr/bin/env python3
"""
check_hosts2.py - Python reimplementation of check_hosts (bash).

Scans local subnets with nmap, maintains per-host logs, and can emit
a daily HTML report (Active, Inactive, Stale) via email.

Usage:
  check_hosts2.py              # run scan only
  check_hosts2.py --daily      # run scan + build and email report
"""

import argparse
import os
import re
import shutil
import socket
import subprocess
from datetime import datetime
from pathlib import Path

# --- Paths and defaults ---
SCRIPT_DIR = Path(__file__).resolve().parent
NMAP_DIR = Path("/var/log/nmap")
NMAP_LOG = NMAP_DIR / "nmap.log"
NMAP_OLD_LOG = NMAP_DIR / "nmap_old.log"
NMAP_TMP = Path("/tmp/nmap_issues")
IP4_RE = re.compile(r"([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})")
HOST_LINE_RE = re.compile(r"Host:\s*" + IP4_RE.pattern)
STALE_AGE_MIN = 60 * 4   # 4 hours
STALE_EMPTY_DAYS = 7
CLEANUP_DAYS = 120
OLD_LOG_MAX_LINES = 2000


def load_config():
    """Load myip.cronmail.config and dyndns-update.config. Return dict of key=value."""
    config = {}
    for name in ("myip.cronmail.config", "dyndns-update.config"):
        p = SCRIPT_DIR / name
        if not p.is_file():
            continue
        with open(p) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    v = v.strip().strip('"').replace("`hostname`", socket.gethostname())
                    v = v.replace("`date +%Y%m`", datetime.now().strftime("%Y%m"))
                    config[k.strip()] = v
    return config


def ensure_nmap_dir():
    NMAP_DIR.mkdir(parents=True, exist_ok=True)


def rotate_logs():
    """Truncate old log to OLD_LOG_MAX_LINES, append current to old, start fresh current."""
    if NMAP_OLD_LOG.exists():
        lines = NMAP_OLD_LOG.read_text().splitlines()
        if len(lines) > OLD_LOG_MAX_LINES:
            NMAP_OLD_LOG.write_text("\n".join(lines[-OLD_LOG_MAX_LINES:]) + "\n")

    if NMAP_LOG.exists():
        with open(NMAP_OLD_LOG, "a") as f:
            f.write(NMAP_LOG.read_text())
        NMAP_LOG.unlink()

    NMAP_LOG.touch()


def _ip_sort_key(ip):
    try:
        return tuple(int(p) for p in ip.split("."))
    except (ValueError, AttributeError):
        return (0, 0, 0, 0)


def _extract_ip(line):
    m = IP4_RE.search(line)
    return m.group(1) if m else None


def _hostname_from_line(line):
    """Extract hostname from 'Host: IP (name)' in nmap -oG line."""
    m = re.search(r"Host:\s*[\d.]+\s*\(([^)]*)\)", line)
    return m.group(1).strip() if m and m.group(1).strip() else ""


def _is_docker_ip(ip):
    """True only if this host routes to ip via docker0 or a br- interface (Docker bridge).
    Uses 'ip route get', so only local Docker networks are detected; 172.x on other VMs is not labeled docker."""
    try:
        r = subprocess.run(
            ["ip", "route", "get", ip],
            capture_output=True, text=True, timeout=2
        )
        out = (r.stdout or "") + (r.stderr or "")
        return "dev docker0" in out or "dev br-" in out
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def _get_last_seen(ip):
    """Last seen from nmap_IP.log: 'Up' not used here; 'Seen YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD HH:MM:SS = new device'.
    Return time only if today, else 'YYYY-MM-DD HH:MM', or ''."""
    p = NMAP_DIR / f"nmap_{ip}.log"
    if not p.exists():
        return ""
    ts_re = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
    try:
        for line in reversed(p.read_text().splitlines()):
            m = ts_re.search(line)
            if m:
                dt = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
                if dt.date() == datetime.now().date():
                    return dt.strftime("%H:%M")
                return dt.strftime("%Y-%m-%d %H:%M")
    except (OSError, ValueError):
        pass
    return ""


def _ip_from_nmap_log_path(path):
    """Extract IP from path like /var/log/nmap/nmap_192.168.1.1.log."""
    m = IP4_RE.search(str(path))
    return m.group(1) if m else None


def _get_stale_4hr_ips():
    """IPs whose nmap_IP.log has not been touched in 4+ hours."""
    try:
        r = subprocess.run(
            ["find", str(NMAP_DIR), "-type", "f", "-name", "nmap_*.log", "-mmin", f"+{STALE_AGE_MIN}"],
            capture_output=True, text=True, timeout=10
        )
        out = set()
        for p in (r.stdout or "").strip().splitlines():
            p = p.strip()
            if "nmap_old" in p or p.endswith("nmap.log"):
                continue
            ip = _ip_from_nmap_log_path(p)
            if ip:
                out.add(ip)
        return out
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return set()


def _get_very_stale_ips():
    """IPs with empty 7+ day logs; also runs find -delete on those files. Pending/nearing deletion."""
    try:
        r = subprocess.run(
            ["find", str(NMAP_DIR), "-type", "f", "-name", "nmap_*.log", "-size", "0", "-mtime", f"+{STALE_EMPTY_DAYS}"],
            capture_output=True, text=True, timeout=10
        )
        paths = [p.strip() for p in (r.stdout or "").splitlines() if p.strip()]
        out = set()
        for p in paths:
            ip = _ip_from_nmap_log_path(p)
            if ip:
                out.add(ip)
        subprocess.run(
            ["find", str(NMAP_DIR), "-type", "f", "-name", "nmap_*.log", "-size", "0", "-mtime", f"+{STALE_EMPTY_DAYS}", "-delete"],
            capture_output=True, timeout=10
        )
        return out
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return set()


def _parse_host_lines(path):
    """Yield (ip, line) for each 'Host: ...' line in path."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        m = HOST_LINE_RE.search(line)
        if m:
            yield m.group(1), line


def scan_subnet(range_spec, nmap_path="/usr/bin/nmap"):
    """Run nmap on range_spec; append 'up' lines to NMAP_LOG and update per-host logs."""
    if range_spec.startswith("10."):
        with open(NMAP_LOG, "a") as f:
            f.write(f"Skipping subnet {range_spec}\n")
        return
    if not IP4_RE.match(range_spec.replace("/24", "").split("/")[0]):
        with open(NMAP_LOG, "a") as f:
            f.write(f"Not scanning {range_spec}\n")
        return

    with open(NMAP_LOG, "a") as f:
        f.write(f"Scanning subnet {range_spec}\n")

    try:
        r = subprocess.run(
            [nmap_path, "-v", "-sn", "--max-parallelism", "100", "--host-timeout", "5", "-oG", "-", range_spec],
            capture_output=True, text=True, timeout=300
        )
        out = (r.stdout or "") + (r.stderr or "")
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as e:
        with open(NMAP_LOG, "a") as f:
            f.write(f"nmap error: {e}\n")
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    seen_ips = set()
    with open(NMAP_LOG, "a") as log:
        for line in out.splitlines():
            if "up" not in line.lower():
                continue
            log.write(line + "\n")
            for ip in IP4_RE.findall(line):
                if ip in seen_ips:
                    continue
                seen_ips.add(ip)
                p = NMAP_DIR / f"nmap_{ip}.log"
                if not p.exists():
                    with open(NMAP_TMP, "a") as tmp:
                        tmp.write(f"{now} = new device {ip}\n")
                    p.write_text(f"{now} = new device {ip}\n")
                with open(p, "a") as f:
                    f.write(f"Seen {now}\n")


def run_scan(nmap_path="/usr/bin/nmap"):
    """Get local IPs and scan each /24."""
    if not shutil.which("nmap"):
        with open(NMAP_LOG, "a") as f:
            f.write("nmap is not installed\n")
        return
    try:
        r = subprocess.run(["hostname", "--all-ip-addresses"], capture_output=True, text=True, check=True)
        ips = [a.strip() for a in r.stdout.split() if a.strip()]
    except (FileNotFoundError, subprocess.CalledProcessError):
        ips = []
    for ip in ips:
        scan_subnet(f"{ip}/24", nmap_path=nmap_path)


def build_report(config, hostname):
    """Build HTML body: Hosts table (IP, Name, Active, Inactive), FreeDNS, RabbitMQ, Failed, MOTD, Uptime."""
    body = []
    body.append("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" \"http://www.w3.org/TR/html4/loose.dtd\">")
    body.append(f"<html><head><title>NMAP Check Hosts - Daily from {hostname}</title>")
    body.append("<style type=\"text/css\">")
    body.append("pre { font-family: \"Courier New\", Courier, monospace; font-size: 10pt; }")
    body.append("p.heading { font-family: Arial, Helvetica, sans-serif; font-size: 12pt; font-weight: bold; color: blue; width:100%; border-bottom: 1px solid black; }")
    body.append("div.data { margin-left:25px; }")
    body.append("table.hosts { border-collapse: collapse; margin: 8px 0; }")
    body.append("table.hosts th, table.hosts td { border: 1px solid #ccc; padding: 4px 8px; text-align: left; }")
    body.append("table.hosts th { background: #eee; }")
    body.append("</style></head><body>")

    # --- Unified Host table (Active, Inactive, Stale combined) ---
    active_ips = {ip for ip, _ in _parse_host_lines(NMAP_LOG)}
    old_ips = {}
    ip_to_hostname = {}
    for ip, line in _parse_host_lines(NMAP_OLD_LOG):
        old_ips[ip] = True
        h = _hostname_from_line(line)
        if h:
            ip_to_hostname[ip] = h
    for ip, line in _parse_host_lines(NMAP_LOG):
        h = _hostname_from_line(line)
        if h:
            ip_to_hostname[ip] = h
    stale_4hr_ips = _get_stale_4hr_ips()
    very_stale_ips = _get_very_stale_ips()
    all_ips = active_ips | set(old_ips) | stale_4hr_ips | very_stale_ips

    body.append("<p class='heading'>Hosts</p><div class='data'>")
    body.append("<table class='hosts'><thead><tr><th>Host IP</th><th>Host Name</th><th>Active</th><th>Inactive</th></tr></thead><tbody>")
    for ip in sorted(all_ips, key=_ip_sort_key):
        hn = "docker" if _is_docker_ip(ip) else ip_to_hostname.get(ip, "")
        if ip in active_ips:
            active = "Up"
            inactive_cell = ""
        else:
            active = _get_last_seen(ip)
            if ip in very_stale_ips:
                inactive_cell = "Very stale"
            elif ip in stale_4hr_ips:
                inactive_cell = "stale"
            else:
                inactive_cell = '<span style="color:red">down</span>'
        body.append(f"<tr><td>{ip}</td><td>{hn}</td><td>{active}</td><td>{inactive_cell}</td></tr>")
    body.append("</tbody></table></div>")

    # --- FreeDNS ---
    freedns = config.get("FREEDNS_LOG", "").strip()
    if freedns and os.path.isfile(freedns):
        body.append("<p class='heading'>FreeDNS</p><div class='data'>")
        try:
            lines = Path(freedns).read_text().splitlines()
            lines = [l for l in lines if "has not changed." not in l][-10:]
            for l in lines:
                l = re.sub(r"([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})", r'<b class="ip">\1</b>', l)
                body.append(f"<p>{l}</p>")
            if lines:
                last = Path(freedns).read_text().strip().splitlines()[-1:] or [""]
                body.append(f"<p>{last[0]}</p>")
        except OSError:
            pass
        body.append("</div>")

    # --- RabbitMQ ---
    rq = Path(f"/var/log/rabbitmq/rabbit@{hostname}.log")
    if rq.is_file():
        body.append("<p class='heading'>RabbitMQ Service Log</p><div class='data'><pre>")
        try:
            tail = rq.read_text().strip().splitlines()[-20:]
            body.append("\n".join(tail))
        except OSError:
            pass
        body.append("</pre></div>")

    # --- Failed services ---
    if shutil.which("systemctl"):
        body.append("<p class='heading'>Failed Services</p><div class='data'>")
        try:
            r = subprocess.run(["systemctl", "list-units", "--state=failed"], capture_output=True, text=True, timeout=5)
            for l in (r.stdout or "").strip().splitlines():
                body.append(f"<p>{l}</p>")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        body.append("</div>")
    else:
        body.append("<p class='heading'>systemd is not available</p>")

    # --- MOTD ---
    if os.path.isfile("/var/run/motd.dynamic"):
        body.append("<p class='heading'>MOTD</p><div class='data'><pre>")
        try:
            body.append(Path("/var/run/motd.dynamic").read_text())
        except OSError:
            pass
        body.append("</pre></div>")

    # --- Uptime ---
    body.append("<p class='heading'>Uptime</p><div class='data'><pre>")
    try:
        r = subprocess.run(["uptime"], capture_output=True, text=True, timeout=2)
        body.append((r.stdout or "").strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    body.append("</pre></div>")

    body.append("</body></html>")

    # MIME envelope
    boundary_val = f"EneUrBrHYB.ABC123/{hostname}.heatherington.ca"
    mime = [
        "This is a MIME-encapsulated message",
        "",
        f"--{boundary_val}",
        "Content-Type: text/html",
        "",
        "\n".join(body),
        "",
        f"--{boundary_val}--",
    ]
    return "\n".join(mime), boundary_val


def run_daily(config, nmap_path="/usr/bin/nmap"):
    hostname = socket.gethostname()
    subject = f"NMAP Check Hosts - Daily from {hostname}"
    to_addr = config.get("MYIP_ADDRESS_TO", "").strip()
    from_addr = config.get("MYIP_ADDRESS_FROM", "").strip()
    if not to_addr:
        print("MYIP_ADDRESS_TO not set in config; skipping mail.")
        return

    html, boundary_val = build_report(config, hostname)
    NMAP_TMP.write_text(html)

    cmd = [
        "mail", to_addr,
        "-s", subject,
        "-a", f"From: {from_addr}" if from_addr else "From: root",
        "-a", "MIME-Version: 1.0",
        "-a", f"Content-Type: multipart/alternative; boundary=\"{boundary_val}\"",
    ]
    try:
        with open(NMAP_TMP) as f:
            subprocess.run(cmd, stdin=f, check=False, timeout=30)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as e:
        print(f"mail failed: {e}")

    dest = NMAP_DIR / f"nmap-{datetime.now().strftime('%Y-%m-%d_%H%M')}.txt"
    try:
        shutil.move(str(NMAP_TMP), str(dest))
    except OSError:
        pass


def cleanup():
    """Remove /var/log/nmap/nmap* files older than CLEANUP_DAYS."""
    try:
        subprocess.run(
            ["find", str(NMAP_DIR), "-maxdepth", "1", "-name", "nmap*", "-mtime", f"+{CLEANUP_DAYS}", "-delete"],
            capture_output=True, timeout=60
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass


def main():
    ap = argparse.ArgumentParser(description="Scan subnets with nmap; --daily to email HTML report (Active, Inactive, Stale).")
    ap.add_argument("-d", "--daily", action="store_true", help="Build and send daily HTML report via mail")
    args = ap.parse_args()

    config = load_config()
    ensure_nmap_dir()

    rotate_logs()
    run_scan()

    if args.daily:
        run_daily(config)

    cleanup()


if __name__ == "__main__":
    main()
