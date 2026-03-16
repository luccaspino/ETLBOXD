import os
import time
import requests
import pandas as pd
from pathlib import Path


TMDB_BASE = "https://api.themoviedb.org/3"
CACHE_PATH = Path("data/tmdb_cache.csv")


def _get_api_key() -> str:
    key = os.getenv("TMDB_API_KEY")
    if not key:
        raise EnvironmentError(
            "TMDB_API_KEY não encontrada. "
            "Defina no arquivo .env ou como variável de ambiente."
        )
    return key


def _search_movie(title: str, year: int, api_key: str) -> int | None:
    """Retorna o tmdb_id do primeiro resultado ou None."""
    params = {
        "api_key": api_key,
        "query": title,
        "year": int(year) if pd.notna(year) else None,
        "language": "pt-BR",
    }
    params = {k: v for k, v in params.items() if v is not None}
    try:
        r = requests.get(f"{TMDB_BASE}/search/movie", params=params, timeout=10)
        r.raise_for_status()
        results = r.json().get("results", [])
        if results:
            return results[0]["id"]
    except Exception as e:
        print(f"[tmdb] erro na busca '{title}': {e}")
    return None


def _get_movie_details(tmdb_id: int, api_key: str) -> dict:
    """Retorna detalhes + créditos em duas chamadas."""
    details = {}
    try:
        r = requests.get(
            f"{TMDB_BASE}/movie/{tmdb_id}",
            params={"api_key": api_key, "language": "pt-BR"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        details["tmdb_id"]           = tmdb_id
        details["tmdb_title"]        = data.get("title")
        details["original_language"] = data.get("original_language")
        details["runtime_min"]       = data.get("runtime")
        details["genres"]            = ", ".join(
            g["name"] for g in data.get("genres", [])
        )
        details["production_countries"] = ", ".join(
            c["iso_3166_1"] for c in data.get("production_countries", [])
        )
        details["tmdb_rating"]       = data.get("vote_average")
        details["tmdb_votes"]        = data.get("vote_count")
        details["poster_path"]       = (
            f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
            if data.get("poster_path") else None
        )
        details["overview"]          = data.get("overview")
        details["tagline"]           = data.get("tagline")
    except Exception as e:
        print(f"[tmdb] erro em detalhes id={tmdb_id}: {e}")

    # Créditos (diretor + top 3 atores)
    try:
        rc = requests.get(
            f"{TMDB_BASE}/movie/{tmdb_id}/credits",
            params={"api_key": api_key},
            timeout=10,
        )
        rc.raise_for_status()
        cdata = rc.json()

        cast = [m["name"] for m in cdata.get("cast", [])[:3]]
        details["cast_top3"] = ", ".join(cast)

        directors = [
            m["name"] for m in cdata.get("crew", [])
            if m.get("job") == "Director"
        ]
        details["director"] = ", ".join(directors)
    except Exception as e:
        print(f"[tmdb] erro em créditos id={tmdb_id}: {e}")

    return details


def load_cache() -> dict[str, dict]:
    if CACHE_PATH.exists():
        df = pd.read_csv(CACHE_PATH)
        return {row["letterboxd_uri"]: row.to_dict() for _, row in df.iterrows()}
    return {}


def save_cache(cache: dict[str, dict]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(list(cache.values())).to_csv(CACHE_PATH, index=False)


def enrich_with_tmdb(master: pd.DataFrame, delay: float = 0.25) -> pd.DataFrame:
    """
    Enriquece o dataframe master com dados do TMDB.
    Usa cache local para evitar re-chamadas entre execuções.
    delay: segundos entre chamadas (respeita rate limit gratuito: 40 req/s).
    """
    api_key = _get_api_key()
    cache = load_cache()

    rows = []
    total = len(master)

    for i, row in master.iterrows():
        uri = row["letterboxd_uri"]

        if uri in cache:
            rows.append(cache[uri])
            continue

        print(f"[tmdb] {i+1}/{total} → {row['title']} ({row.get('year', '?')})")

        tmdb_id = _search_movie(row["title"], row.get("year"), api_key)
        if tmdb_id:
            details = _get_movie_details(tmdb_id, api_key)
        else:
            details = {"tmdb_id": None}

        details["letterboxd_uri"] = uri
        cache[uri] = details
        rows.append(details)

        # Salva cache a cada 50 filmes
        if (i + 1) % 50 == 0:
            save_cache(cache)
            print(f"[tmdb] cache salvo ({i+1} filmes processados)")

        time.sleep(delay)

    save_cache(cache)
    print(f"[tmdb] concluído. Cache salvo em {CACHE_PATH}")

    tmdb_df = pd.DataFrame(rows)
    enriched = master.merge(tmdb_df, on="letterboxd_uri", how="left")
    return enriched
