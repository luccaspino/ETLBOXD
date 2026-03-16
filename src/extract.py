import pandas as pd
from pathlib import Path


RAW_DIR = Path("raw")


def load_csv(filename: str) -> pd.DataFrame:
    path = RAW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    df = pd.read_csv(path)
    print(f"[extract] {filename}: {len(df)} linhas, colunas: {list(df.columns)}")
    return df


def extract_all() -> dict[str, pd.DataFrame]:
    return {
        "diary":     load_csv("diary.csv"),
        "ratings":   load_csv("ratings.csv"),
        "watched":   load_csv("watched.csv"),
        "watchlist": load_csv("watchlist.csv"),
        "reviews":   load_csv("reviews.csv"),
    }
