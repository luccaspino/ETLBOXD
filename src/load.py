import pandas as pd
from pathlib import Path


PROCESSED_DIR = Path("data/processed")


def save_csv(df: pd.DataFrame, name: str) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / f"{name}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"[load] salvo: {path} ({len(df)} linhas)")


def save_all(transformed: dict[str, pd.DataFrame]) -> None:
    for name, df in transformed.items():
        save_csv(df, name)

    print("\n[load] todos os arquivos salvos em data/processed/")
    print("       Conecte o Power BI a esta pasta para montar o dashboard.")

