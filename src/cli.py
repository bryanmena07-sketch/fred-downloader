"""Simple CLI for downloading FRED series and (optionally) running a scheduler."""
import argparse
import os
import sys
from datetime import datetime
from typing import List

from dotenv import load_dotenv

from fred_downloader import FredDownloader


def parse_args():
    p = argparse.ArgumentParser(description="Download monthly FRED series to CSV")
    p.add_argument("--series", "-s", nargs='*', help="One or more FRED series ids (e.g. PAYEMS UNRATE)")
    p.add_argument("--preset", choices=["employment"], help="Use a preset list of series (e.g. 'employment')")
    p.add_argument("--start", help="Start date YYYY-MM-DD", default=None)
    p.add_argument("--end", help="End date YYYY-MM-DD", default=None)
    p.add_argument("--out", "-o", help="Output CSV path", default="data.csv")
    p.add_argument("--api-key", help="FRED API key (env FRED_API_KEY used if omitted)")
    p.add_argument("--daemon", action="store_true", help="Run as a long-running scheduler")
    p.add_argument("--daily", help="If --daemon, daily time in HH:MM (local) to run", default="09:00")
    return p.parse_args()


def run_job(api_key: str, series: List[str], start: str, end: str, out: str):
    downloader = FredDownloader(api_key)
    df = downloader.fetch_multiple(series, start, end)
    downloader.save_csv(df, out)
    print(f"Saved CSV to {out}")


def main():
    load_dotenv()
    args = parse_args()
    api_key = args.api_key or os.getenv("FRED_API_KEY")
    if not api_key:
        print("FRED API key not provided. Set FRED_API_KEY or pass --api-key.")
        sys.exit(1)

    # determine series list: explicit series take precedence, otherwise use preset
    preset_lists = {
        # employment preset: total nonfarm payrolls and unemployment rate
        "employment": ["PAYEMS", "UNRATE"],
    }

    series = args.series or []
    if args.preset:
        preset = preset_lists.get(args.preset, [])
        # if user supplied explicit series, extend with preset (avoid duplicates)
        if series:
            series = list(dict.fromkeys(series + preset))
        else:
            series = preset
    start = args.start
    end = args.end
    out = args.out

    if not args.daemon:
        run_job(api_key, series, start, end, out)
        return

    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.cron import CronTrigger

    hour, minute = [int(x) for x in args.daily.split(":")]
    trigger = CronTrigger(hour=hour, minute=minute)
    scheduler = BlockingScheduler()

    def job():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base, ext = os.path.splitext(out)
        out_path = f"{base}_{timestamp}{ext or '.csv'}"
        run_job(api_key, series, start, end, out_path)

    scheduler.add_job(job, trigger)
    print(f"Scheduler started — running daily at {args.daily}. Ctrl+C to exit.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped")


if __name__ == "__main__":
    main()
