"""
Normalização do master.csv em modelo estrela.

Gera em data/processed/:
  genres.csv          (genre_id, genre_name)
  film_genres.csv     (film_id, genre_id)

  countries.csv       (country_id, country_code)
  film_countries.csv  (film_id, country_id)

  directors.csv       (director_id, director_name)
  film_directors.csv  (film_id, director_id)

  actors.csv          (actor_id, actor_name)
  film_actors.csv     (film_id, actor_id, billing_order)
"""

import pandas as pd
from pathlib import Path


PROCESSED_DIR = Path("data/processed")


def _save(df: pd.DataFrame, name: str) -> None:
    path = PROCESSED_DIR / f"{name}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"[normalize] {name}.csv → {len(df)} linhas")


def _explode_column(
    master: pd.DataFrame,
    col: str,
    id_col: str,
    name_col: str,
    sep: str = ", ",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Explode uma coluna de valores separados por vírgula.
    Retorna (dim_df, bridge_df).
    """
    exploded = (
        master[["film_id", col]]
        .dropna(subset=[col])
        .copy()
    )
    exploded[col] = exploded[col].str.split(sep)
    exploded = exploded.explode(col)
    exploded[col] = exploded[col].str.strip()
    exploded = exploded[exploded[col] != ""]

    # Dimensão — valores únicos com ID sequencial
    unique_vals = sorted(exploded[col].unique())
    dim_df = pd.DataFrame({
        id_col:   range(1, len(unique_vals) + 1),
        name_col: unique_vals,
    })

    # Tabela ponte
    bridge_df = (
        exploded
        .merge(dim_df, left_on=col, right_on=name_col)
        [["film_id", id_col]]
        .drop_duplicates()
        .sort_values(["film_id", id_col])
        .reset_index(drop=True)
    )

    return dim_df, bridge_df


def _explode_actors(master: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Igual ao _explode_column mas preserva billing_order (posição no elenco).
    """
    exploded = (
        master[["film_id", "cast_top3"]]
        .dropna(subset=["cast_top3"])
        .copy()
    )
    exploded["cast_top3"] = exploded["cast_top3"].str.split(", ")
    exploded = exploded.explode("cast_top3")
    exploded["cast_top3"] = exploded["cast_top3"].str.strip()
    exploded = exploded[exploded["cast_top3"] != ""].copy()

    # billing_order por posição dentro de cada filme
    exploded["billing_order"] = exploded.groupby("film_id").cumcount() + 1

    unique_actors = sorted(exploded["cast_top3"].unique())
    actors_df = pd.DataFrame({
        "actor_id":   range(1, len(unique_actors) + 1),
        "actor_name": unique_actors,
    })

    bridge_df = (
        exploded
        .merge(actors_df, left_on="cast_top3", right_on="actor_name")
        [["film_id", "actor_id", "billing_order"]]
        .drop_duplicates(subset=["film_id", "actor_id"])
        .sort_values(["film_id", "billing_order"])
        .reset_index(drop=True)
    )

    return actors_df, bridge_df


def normalize(master_path: str = "data/processed/master.csv") -> None:
    master = pd.read_csv(master_path)
    print(f"[normalize] master carregado: {len(master)} filmes\n")

    # Gêneros
    genres_df, film_genres_df = _explode_column(
        master, "genres", "genre_id", "genre_name"
    )
    _save(genres_df, "genres")
    _save(film_genres_df, "film_genres")

    # Países
    countries_df, film_countries_df = _explode_column(
        master, "production_countries", "country_id", "country_code", sep=", "
    )
    _save(countries_df, "countries")
    _save(film_countries_df, "film_countries")

    # Diretores
    directors_df, film_directors_df = _explode_column(
        master, "director", "director_id", "director_name", sep=", "
    )
    _save(directors_df, "directors")
    _save(film_directors_df, "film_directors")

    # Atores
    actors_df, film_actors_df = _explode_actors(master)
    _save(actors_df, "actors")
    _save(film_actors_df, "film_actors")

    print("\n[normalize] concluído. Modelo estrela pronto para o Power BI.")

