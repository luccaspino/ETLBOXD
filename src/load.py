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


# Opcional: salvar em DuckDB para queries SQL
def save_duckdb(transformed: dict[str, pd.DataFrame], db_path: str = "data/letterboxd.duckdb") -> None:
    try:
        import duckdb
        con = duckdb.connect(db_path)
        for name, df in transformed.items():
            con.execute(f"DROP TABLE IF EXISTS {name}")
            con.execute(f"CREATE TABLE {name} AS SELECT * FROM df")
            print(f"[load] duckdb → tabela '{name}' ({len(df)} linhas)")
        con.close()
        print(f"[load] banco salvo em {db_path}")
    except ImportError:
        print("[load] duckdb não instalado — pulando. Use: pip install duckdb")
