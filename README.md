# FRED Monthly Employment Downloader

Small Python utility to download monthly series from FRED (Federal Reserve Economic Data) and save as CSV.

Quick start

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Set your FRED API key (obtain one at https://fred.stlouisfed.org/)

```bash
export FRED_API_KEY=your_api_key_here
```

3. Download example series (PAYEMS) or use the `employment` preset:

```bash
python -m src.cli --series PAYEMS --start 2010-01-01 --end 2026-04-01 --out payems.csv
# or use preset
python -m src.cli --preset employment --start 2010-01-01 --end 2026-04-01 --out employment.csv
```

4. Install a daily cron job (helper):

```bash
python tools/install_cron.py --daily 09:00 --command "/full/path/.venv/bin/python /full/path/src/cli.py --preset employment --start 2010-01-01 --end $(date +%Y-%m-%d) --out /full/path/data/employment.csv" --install
```
