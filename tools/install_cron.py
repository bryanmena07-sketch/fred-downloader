"""Install a simple daily cron entry for the downloader.

Usage examples:
  # Install a daily 09:00 job that runs the CLI
  python tools/install_cron.py --daily 09:00 --command "/full/path/.venv/bin/python /full/path/src/cli.py --preset employment --start 2010-01-01 --end $(date +%Y-%m-%d) --out /full/path/data/employment.csv" --install

  # Print the cron line without installing
  python tools/install_cron.py --daily 09:00 --command "echo hello" 
"""
import argparse
import subprocess
import sys


def parse_args():
    p = argparse.ArgumentParser(description="Install a daily cron job for the downloader")
    p.add_argument("--daily", help="Daily time in HH:MM")
    p.add_argument("--command", required=True, help="Full command to run (use absolute paths)")
    p.add_argument("--install", action="store_true", help="If set, install into user's crontab")
    return p.parse_args()


def make_cron_line(daily: str, command: str) -> str:
    hh, mm = daily.split(":")
    return f"{int(mm)} {int(hh)} * * * {command}"


def install_cron(line: str):
    # read existing crontab (if any)
    try:
        existing = subprocess.run(["crontab", "-l"], check=False, capture_output=True, text=True)
        current = existing.stdout if existing.returncode == 0 else ""
    except FileNotFoundError:
        print("crontab command not found on this system")
        sys.exit(1)

    if line in current:
        print("Cron line already present, nothing to do.")
        return

    new_cron = current.rstrip() + "\n" + line + "\n"
    p = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
    p.communicate(new_cron)
    if p.returncode == 0:
        print("Installed cron job.")
    else:
        print("Failed to install cron job.")


def main():
    args = parse_args()
    if not args.daily:
        print("--daily is required (HH:MM)")
        sys.exit(1)

    line = make_cron_line(args.daily, args.command)
    print("Cron line:")
    print(line)
    if args.install:
        install_cron(line)


if __name__ == "__main__":
    main()
