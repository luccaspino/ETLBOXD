"""
Letterboxd ETL Pipeline
=======================
Uso:
    python main.py                  # roda ETL completo com enriquecimento TMDB
    python main.py --skip-tmdb      # pula TMDB (útil para testar a pipeline local)
    python main.py --duckdb         # salva também em DuckDB além dos CSVs
"""

import argparse
from dotenv import load_dotenv

from src.extract import extract_all
from src.transform import transform_all
from src.tmdb import enrich_with_tmdb
from src.load import save_all, save_duckdb


def main(skip_tmdb: bool = False, use_duckdb: bool = False) -> None:
    load_dotenv()

    print("=" * 50)
    print("LETTERBOXD ETL — iniciando")
    print("=" * 50)

    # 1. Extract
    print("\n[1/3] EXTRACT")
    raw = extract_all()

    # 2. Transform
    print("\n[2/3] TRANSFORM")
    transformed = transform_all(raw)

    # 3. Enriquecer com TMDB
    if not skip_tmdb:
        print("\n[2.5] TMDB ENRICHMENT")
        transformed["master"] = enrich_with_tmdb(transformed["master"])
        transformed["watchlist"] = enrich_with_tmdb(transformed["watchlist"])
    else:
        print("\n[2.5] TMDB — pulado (--skip-tmdb)")

    # 4. Load
    print("\n[3/3] LOAD")
    save_all(transformed)

    if use_duckdb:
        save_duckdb(transformed)

    print("\n✓ Pipeline concluída com sucesso!")
    print("  Arquivos em: data/processed/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Letterboxd ETL Pipeline")
    parser.add_argument("--skip-tmdb", action="store_true", help="Pula enriquecimento TMDB")
    parser.add_argument("--duckdb", action="store_true", help="Salva também em DuckDB")
    args = parser.parse_args()

    main(skip_tmdb=args.skip_tmdb, use_duckdb=args.duckdb)
