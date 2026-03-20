# Letterboxd ETL Pipeline

Pipeline de dados que extrai o histórico de filmes do Letterboxd, transforma e enriquece com metadados da API do TMDB, e carrega os dados processados para análise em Power BI.


O ETLBOXD é uma pipeline ETL pessoal que transforma dados brutos exportados do Letterboxd em um dashboard analítico interativo. O projeto parte dos CSVs gerados pela plataforma — histórico assistido, notas, diário, watchlist e críticas — e os enriquece com metadados da API do TMDB, adicionando gênero, duração, país de produção, idioma original, nota do público, sinopse, diretor e top 3 atores de cada filme.
A pipeline foi desenvolvida em Python com pandas, organizada em três etapas: extração dos CSVs, transformação e limpeza dos dados com construção de um modelo estrela normalizado, e carga em arquivos processados prontos para consumo. O projeto conta com cache local para evitar chamadas desnecessárias à API e está dockerizado para facilitar a execução em qualquer ambiente.
No Power BI, os dados são carregados seguindo o modelo estrela com tabelas dimensão para gêneros, países, diretores e atores, conectadas ao fato central via tabelas ponte. Duas tabelas calendário complementam o modelo — uma para data de exibição e outra para ano de lançamento. As medidas DAX calculam KPIs como total de filmes, horas consumidas, médias de nota e o comparativo entre a avaliação pessoal e a nota do público no TMDB.

## Estrutura do projeto

```
letterboxd-etl/
├── data/
│   ├── raw/              ← CSVs exportados do Letterboxd (não versionados)
│   └── processed/        ← saída da pipeline (conectar ao Power BI)
├── src/
│   ├── extract.py        ← leitura e validação dos CSVs
│   ├── transform.py      ← limpeza, tipagem e merge
│   ├── tmdb.py           ← enriquecimento via API do TMDB
│   ├── normalize.py      ← normalização em modelo estrela
│   └── load.py           ← escrita dos CSVs processados / DuckDB
├── main.py               ← entrypoint da pipeline
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── requirements.txt
└── README.md
```

## Dados de entrada

Exportar dados em: [letterboxd.com/settings/data](https://letterboxd.com/settings/data)

Arquivos utilizados:
| Arquivo | Conteúdo |
|---|---|
| `watched.csv` | Todos os filmes assistidos |
| `ratings.csv` | Notas atribuídas (0.5 a 5) |
| `diary.csv` | Diário com data, nota, rewatch e tags |
| `watchlist.csv` | Filmes na lista de quero ver |
| `reviews.csv` | Críticas escritas |

## Dados enriquecidos via TMDB

Para cada filme, a pipeline busca na API do TMDB:

- Gêneros
- Duração (minutos)
- País de produção
- Idioma original
- Nota e número de votos no TMDB
- URL do poster
- Sinopse e tagline
- Diretor
- Top 3 atores do elenco

## Setup

### Com Docker 


# 1. Clone o repositório
git clone https://github.com/seu-usuario/letterboxd-etl
cd letterboxd-etl

# 2. Configure a chave da API do TMDB
cp .env.example .env
# Edite .env e insira sua TMDB_API_KEY
# Chave gratuita em: https://www.themoviedb.org/settings/api

# 3. Coloque os CSVs do Letterboxd em data/raw/

# 4. Rode
docker compose up


### Sem Docker

pip install -r requirements.txt
cp .env.example .env
# edite .env com sua TMDB_API_KEY
python main.py

## Opções de execução

python main.py                  # pipeline completa com TMDB
python main.py --skip-tmdb      # pula TMDB (teste local sem API key)
python main.py --duckdb         # salva também em DuckDB


## Modelo estrela — saída da pipeline


master.csv (fato)
    │
    ├── film_genres.csv    → genres.csv
    ├── film_countries.csv → countries.csv
    ├── film_directors.csv → directors.csv
    └── film_actors.csv    → actors.csv


Relacionamentos a criar no Power BI:
- `master[film_id]` → `film_genres[film_id]` → `genres[genre_id]`
- `master[film_id]` → `film_countries[film_id]` → `countries[country_id]`
- `master[film_id]` → `film_directors[film_id]` → `directors[director_id]`
- `master[film_id]` → `film_actors[film_id]` → `actors[actor_id]`

## Cache TMDB

Os resultados são salvos em `data/tmdb_cache.csv`. Rodar a pipeline novamente só buscará filmes ainda não cacheados.

## Tecnologias

- Python 3.11
- pandas
- requests
- python-dotenv
- duckdb (opcional)
- Docker
- Power BI Desktop


---------------------------

