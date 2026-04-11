import os
from typing import List, Optional

import pandas as pd
import requests


class FredDownloader:
    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("FRED API key required")
        self.api_key = api_key

    def fetch_series(self, series_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
        }
        if start_date:
            params["observation_start"] = start_date
        if end_date:
            params["observation_end"] = end_date

        resp = requests.get(self.BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        obs = data.get("observations", [])

        df = pd.DataFrame(obs)
        if df.empty:
            return pd.DataFrame(columns=["date", series_id])

        df = df[["date", "value"]].rename(columns={"value": series_id})
        df[series_id] = pd.to_numeric(df[series_id].replace('.', pd.NA))
        df["date"] = pd.to_datetime(df["date"]).dt.date
        return df

    def fetch_multiple(self, series_ids: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        frames = []
        for sid in series_ids:
            df = self.fetch_series(sid, start_date, end_date)
            df = df.set_index("date")
            frames.append(df)

        if not frames:
            return pd.DataFrame()

        merged = pd.concat(frames, axis=1, join="outer").sort_index()
        merged.index.name = "date"
        return merged.reset_index()

    def save_csv(self, df: pd.DataFrame, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        df.to_csv(path, index=False)
