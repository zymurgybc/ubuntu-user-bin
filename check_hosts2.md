# check_hosts2.py

Python 3 reimplementation of the `check_hosts` bash script. It scans local subnets with nmap, maintains per-host logs, and can send a daily HTML report (Active, Inactive, Stale) via email.

---

## Usage

```bash
check_hosts2.py              # run scan only
check_hosts2.py -d           # run scan + build and email report
check_hosts2.py --daily      # same as -d
```

| Invocation       | Effect |
|------------------|--------|
| (no args)        | Rotate logs, run nmap on each local /24, update per-host logs, clean old files. |
| `-d`, `--daily`  | Same as no-args, then build an HTML report, send it with `mail`, and move the report to `/var/log/nmap/nmap-YYYY-MM-DD_HHMM.txt`. |

---

## Requirements

- **Python 3** (stdlib only: `argparse`, `os`, `pathlib`, `re`, `shutil`, `socket`, `subprocess`, `datetime`)
- **nmap** (`/usr/bin/nmap`)
- **hostname** (for `hostname --all-ip-addresses`)
- **mail** (or compatible) for `-d` / `--daily`
- **find** (for stale detection and cleanup)

---

## Configuration

Config files are read from the script directory (`~/bin/` when the script lives there). Both are optional; missing files are ignored.

### myip.cronmail.config

Used for the daily email. Format: `KEY=value` (one per line; `#` lines ignored).

| Variable            | Purpose |
|---------------------|---------|
| `MYIP_ADDRESS_TO`   | Recipient for the report. Required for `-d` / `--daily`; if unset, mail is skipped. |
| `MYIP_ADDRESS_FROM` | `From` header. If unset, `From: root` is used. |

### dyndns-update.config

| Variable     | Purpose |
|--------------|---------|
| `FREEDNS_LOG` | Path to FreeDNS log. If set and the file exists, its last 10 lines (excluding "has not changed.") and the last line are included in the report. |

### Variable substitution

In both configs, values may contain:

- `` `hostname` `` → current hostname
- `` `date +%Y%m` `` → `YYYYMM` for the current date

---

## Paths and files

| Path | Purpose |
|------|---------|
| `/var/log/nmap/` | Working directory: `nmap.log`, `nmap_old.log`, `nmap_<ip>.log`, `nmap-YYYY-MM-DD_HHMM.txt` |
| `/var/log/nmap/nmap.log` | Current scan output (grepable `-oG`); overwritten each run. |
| `/var/log/nmap/nmap_old.log` | Previous run: last 2000 lines kept; current `nmap.log` is appended before each scan. |
| `/var/log/nmap/nmap_<ip>.log` | Per-host log: “new device” on first see, then “Seen <timestamp>” on each see. |
| `/tmp/nmap_issues` | During scan: “new device” lines. With `-d` / `--daily`, it is overwritten by the full MIME report before sending, then moved to `nmap-YYYY-MM-DD_HHMM.txt`. |
| `/var/log/nmap/nmap-YYYY-MM-DD_HHMM.txt` | Archived daily report (`-d` / `--daily`) (MIME + HTML). |

---

## Constants (in script)

| Constant | Value | Meaning |
|----------|-------|---------|
| `STALE_AGE_MIN` | 240 | Stale “untouched” threshold: 4 hours (minutes). |
| `STALE_EMPTY_DAYS` | 7 | Empty per-host logs older than this are listed in “Stale hosts (will delete)” and then deleted. |
| `CLEANUP_DAYS` | 120 | `/var/log/nmap/nmap*` files older than this are removed at the end of each run. |
| `OLD_LOG_MAX_LINES` | 2000 | `nmap_old.log` is truncated to this many lines before appending the current `nmap.log`. |

---

## Scan behavior

1. **Log rotation**
   - If `nmap_old.log` has more than 2000 lines, it is truncated to the last 2000.
   - If `nmap.log` exists, it is appended to `nmap_old.log` and then removed.
   - A new empty `nmap.log` is created.

2. **Local IPs**
   - `hostname --all-ip-addresses` is run; each token is treated as an interface address.

3. **Per-address scan**
   - For each address, the script runs:  
     `nmap -v -sn --max-parallelism 100 --host-timeout 5 -oG - <ip>/24`
   - Subnets starting with `10.` are skipped (only logged).
   - Non‑IPv4 or invalid ranges are skipped (only logged).

4. **Processing nmap output**
   - Only lines containing `up` (case‑insensitive) are appended to `nmap.log`.
   - IPv4 addresses are extracted with a regex; for each:
     - If `nmap_<ip>.log` does not exist: write “new device” to `/tmp/nmap_issues` and create `nmap_<ip>.log` with that line.
     - Append “Seen <timestamp>” to `nmap_<ip>.log`.

5. **Cleanup**
   - `find /var/log/nmap -maxdepth 1 -name 'nmap*' -mtime +120 -delete` is run.

---

## Daily report (`-d` / `--daily`)

The report is built as a MIME multipart message with an HTML body and is sent with `mail` using `-a` for `From`, `MIME-Version`, and `Content-Type` (with boundary). The same MIME is written to `/tmp/nmap_issues`, then moved to `/var/log/nmap/nmap-YYYY-MM-DD_HHMM.txt`.

### Section order

1. **Hosts** (single table)
   - One table with columns: **Host IP**, **Host Name**, **Active**, **Inactive**.
   - One row per known IP (from current and old `nmap.log`, plus stale 4hr and very-stale sets). Sorted by IP.
   - **Host Name**: `docker` only when verified: `ip route get <ip>` shows the route via `dev docker0` or `dev br-` on this host (i.e. the IP is on a local Docker network). Other 172.x or VM addresses are not assumed to be Docker. Otherwise the name from `Host: IP (name)` in nmap `-oG` output, or blank.
   - **Active**: `Up` if the host is in the current scan; otherwise the last-seen time from `nmap_<ip>.log` (time only if today, else `YYYY-MM-DD HH:MM`), or blank if unknown.
   - **Inactive**: blank when the host is up; when not up: `down` (in red) if simply missing from the current scan; `stale` if its `nmap_<ip>.log` has not been touched in 4+ hours; `Very stale` if it has an empty 7+‑day log (pending/nearing deletion; those files are deleted after listing).

2. **FreeDNS** (optional, with heading)
   - Heading: **FreeDNS**. If `FREEDNS_LOG` is set and the file exists: last 10 lines excluding “has not changed.”, IPs wrapped in `<b class="ip">`, plus the file’s last line, inside `<div class='data'>`.

3. **RabbitMQ Service Log** (optional)
   - If `/var/log/rabbitmq/rabbit@<hostname>.log` exists: last 20 lines in a `<pre>` block.

4. **Failed Services**
   - If `systemctl` exists: `systemctl list-units --state=failed`, each line in a `<p>`.  
   - Otherwise: “systemd is not available”.

5. **MOTD** (optional)
   - If `/var/run/motd.dynamic` exists: its contents in a `<pre>` block.

6. **Uptime**
   - Output of `uptime` in a `<pre>` block.

---

## Functions (overview)

| Function | Role |
|----------|------|
| `load_config()` | Load `myip.cronmail.config` and `dyndns-update.config`; substitute `` `hostname` `` and `` `date +%Y%m` ``; return a dict. |
| `ensure_nmap_dir()` | Create `/var/log/nmap` if missing. |
| `rotate_logs()` | Truncate `nmap_old.log`, append `nmap.log` into it, remove `nmap.log`, touch new `nmap.log`. |
| `scan_subnet(range_spec, nmap_path)` | Run nmap on `range_spec`, append “up” lines to `nmap.log`, update or create `nmap_<ip>.log` and optionally `/tmp/nmap_issues`. |
| `run_scan(nmap_path)` | Resolve local IPs via `hostname --all-ip-addresses` and run `scan_subnet` for each `/24`. |
| `_hostname_from_line(line)` | Extract hostname from `Host: IP (name)` in nmap `-oG` line. |
| `_is_docker_ip(ip)` | Run `ip route get <ip>`; return True only if route uses `dev docker0` or `dev br-` (local Docker). |
| `_get_last_seen(ip)` | From `nmap_<ip>.log`, return last “Seen” or “new device” time; time only if today, else `YYYY-MM-DD HH:MM`, or `''`. |
| `_ip_from_nmap_log_path(path)` | Extract IP from a path like `nmap_1.2.3.4.log`. |
| `_get_stale_4hr_ips()` | Set of IPs whose `nmap_<ip>.log` has mtime &gt; 4 hours. |
| `_get_very_stale_ips()` | Set of IPs with empty 7+‑day `nmap_<ip>.log`; also runs `find -delete` on those files. |
| `build_report(config, hostname)` | Build the HTML report (Hosts table, FreeDNS, RabbitMQ, Failed, MOTD, Uptime) and MIME envelope; return `(mime_string, boundary)`. |
| `run_daily(config, nmap_path)` | Build report, write to `/tmp/nmap_issues`, run `mail`, move to `nmap-YYYY-MM-DD_HHMM.txt`. |
| `cleanup()` | `find /var/log/nmap -maxdepth 1 -name 'nmap*' -mtime +120 -delete`. |
| `main()` | Parse `-d` / `--daily`, load config, ensure dir, rotate, run_scan, run_daily if `-d` / `--daily`, cleanup. |

---

## Implementation notes

- **Hosts table**: One row per known IP. **Host Name** is `docker` only when `_is_docker_ip(ip)` is true: `ip route get <ip>` shows routing via `dev docker0` or `dev br-` on this host (local Docker networks). 172.x or other private IPs on remote VMs are not labeled docker. **Active** is `Up` or last-seen; **Inactive** is `down` (red), `stale`, or `Very stale` when the host is not up.
- **Stale / Very stale**: `_get_very_stale_ips()` runs `find -delete` on empty 7+‑day logs; those IPs are still shown in the table as “Very stale” before the delete.
- **RabbitMQ path**: Uses `socket.gethostname()`, e.g. `/var/log/rabbitmq/rabbit@<hostname>.log`.
- **FreeDNS**: Has its own **FreeDNS** heading and `<div class='data'>` block.
- **Config**: Same `KEY=value` style and placeholders as the original `check_hosts` bash script; missing files or keys are handled without failing the script.
