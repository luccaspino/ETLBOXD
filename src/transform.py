import pandas as pd


def clean_diary(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Watched Date"] = pd.to_datetime(df["Watched Date"], errors="coerce")
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df["Rewatch"] = df["Rewatch"].fillna("").str.strip().str.upper() == "YES"
    df["Tags"] = df["Tags"].fillna("")
    df = df.rename(columns={
        "Date": "log_date",
        "Name": "title",
        "Year": "year",
        "Letterboxd URI": "letterboxd_uri",
        "Rating": "rating",
        "Rewatch": "is_rewatch",
        "Tags": "tags",
        "Watched Date": "watched_date",
    })
    return df


def clean_ratings(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df = df.rename(columns={
        "Date": "rated_date",
        "Name": "title",
        "Year": "year",
        "Letterboxd URI": "letterboxd_uri",
        "Rating": "rating",
    })
    return df


def clean_watched(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    df = df.rename(columns={
        "Date": "watched_date",
        "Name": "title",
        "Year": "year",
        "Letterboxd URI": "letterboxd_uri",
    })
    return df


def clean_watchlist(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    df = df.rename(columns={
        "Date": "added_date",
        "Name": "title",
        "Year": "year",
        "Letterboxd URI": "letterboxd_uri",
    })
    return df


def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Watched Date"] = pd.to_datetime(df["Watched Date"], errors="coerce")
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df["Rewatch"] = df["Rewatch"].fillna("").str.strip().str.upper() == "YES"
    df["Review"] = df["Review"].fillna("")
    df["word_count"] = df["Review"].apply(lambda x: len(x.split()) if x else 0)
    df = df.rename(columns={
        "Date": "log_date",
        "Name": "title",
        "Year": "year",
        "Letterboxd URI": "letterboxd_uri",
        "Rating": "rating",
        "Rewatch": "is_rewatch",
        "Review": "review_text",
        "Tags": "tags",
        "Watched Date": "watched_date",
    })
    return df


def build_master(
    diary: pd.DataFrame,
    ratings: pd.DataFrame,
    watched: pd.DataFrame,
) -> pd.DataFrame:
    base = watched[["title", "year", "letterboxd_uri", "watched_date"]].drop_duplicates(
        subset=["letterboxd_uri"]
    )
    ratings_dedup = ratings[["letterboxd_uri", "rating"]].drop_duplicates(
        subset=["letterboxd_uri"]
    )
    master = base.merge(ratings_dedup, on="letterboxd_uri", how="left")

    diary_extra = diary[["letterboxd_uri", "is_rewatch", "tags"]].drop_duplicates(
        subset=["letterboxd_uri"]
    )
    master = master.merge(diary_extra, on="letterboxd_uri", how="left")
    master["is_rewatch"] = master["is_rewatch"].fillna(False)
    master["tags"] = master["tags"].fillna("")

    master = master.sort_values("watched_date").reset_index(drop=True)
    master["film_id"] = master.index + 1

    return master


def add_film_id(df: pd.DataFrame, master: pd.DataFrame) -> pd.DataFrame:
    """Adiciona film_id em qualquer tabela que tenha letterboxd_uri."""
    uri_to_id = master[["letterboxd_uri", "film_id"]].drop_duplicates()
    return df.merge(uri_to_id, on="letterboxd_uri", how="left")


def transform_all(raw: dict) -> dict[str, pd.DataFrame]:
    diary     = clean_diary(raw["diary"])
    ratings   = clean_ratings(raw["ratings"])
    watched   = clean_watched(raw["watched"])
    watchlist = clean_watchlist(raw["watchlist"])
    reviews   = clean_reviews(raw["reviews"])

    master = build_master(diary, ratings, watched)

    # Adiciona film_id nas tabelas que têm letterboxd_uri
    diary     = add_film_id(diary, master)
    reviews   = add_film_id(reviews, master)
    # watchlist não tem film_id pois os filmes ainda não foram assistidos
    # mas pode ter tmdb_id após enriquecimento — deixamos sem film_id

    print(f"[transform] master: {len(master)} filmes únicos")
    print(f"[transform] com nota: {master['rating'].notna().sum()}")
    print(f"[transform] rewatches: {master['is_rewatch'].sum()}")
    print(f"[transform] diary com film_id: {diary['film_id'].notna().sum()}/{len(diary)}")
    print(f"[transform] reviews com film_id: {reviews['film_id'].notna().sum()}/{len(reviews)}")

    return {
        "master":    master,
        "diary":     diary,
        "watchlist": watchlist,
        "reviews":   reviews,
    }