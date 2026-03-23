# 🎬 Letterboxd ETL Pipeline & Dashboard

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Power Bi](https://img.shields.io/badge/power_bi-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)


> Uma pipeline de dados automatizada que extrai seu histórico do Letterboxd, enriquece com metadados da API do TMDB e modela os dados para um Dashboard analítico no Power BI.

Incluindo 4 páginas: Visão Geral, DireAtor, Explorar de filmes assistidos, Explorar de filmes na watchlist.

<img width="1100" height="625" alt="image" src="https://github.com/user-attachments/assets/7ba6242c-0dbf-41d2-bdf6-fddbc3f84b23" />
<img width="1108" height="467" alt="image" src="https://github.com/user-attachments/assets/c55638ed-8e27-4bdc-843c-4d2611343196" />
<img width="1087" height="614" alt="image" src="https://github.com/user-attachments/assets/3b410e2b-c156-48f0-a4bf-cacb48b549a9" />
<img width="1113" height="580" alt="image" src="https://github.com/user-attachments/assets/231675b2-54cc-4703-900d-967b9a001558" />

Modelagem estrela:

<img width="1107" height="668" alt="image" src="https://github.com/user-attachments/assets/e8b9808e-fa0a-4732-917f-9bef13fcb6b6" />

## 📌 Sobre o Projeto

O **ETLBOXD** é uma pipeline ETL pessoal que transforma dados brutos exportados do Letterboxd em um dashboard analítico interativo. O projeto parte dos CSVs gerados pela plataforma — *histórico assistido, notas, diário, watchlist e críticas* — e os enriquece com metadados da API do TMDB. 

A pipeline foi desenvolvida em **Python com Pandas** e organizada em três etapas: 
1. **Extract**: Extração e leitura dos CSVs brutos do Letterboxd.
2. **Transform & TMDB API**: Enriquecimento dos dados buscando gênero, duração, país de produção, idioma, sinopse, diretor e top 3 atores.
3. **Load**: Normalização em modelo estrela e carga em arquivos processados prontos para consumo. 

O projeto conta com **cache local** para evitar chamadas desnecessárias à API e está **Dockerizado** para facilitar a execução em qualquer ambiente.

---

## 🏗️ Estrutura do Projeto

```
letterboxd-etl/
├── data/
│   ├── raw/              ← CSVs exportados do Letterboxd (cole aqui seus dados)
│   └── processed/        ← Saída da pipeline (tabelas fato e dimensão)
├── src/
│   ├── BI/               ← Template do Power BI (.pbit) pronto para uso
│   ├── extract.py        ← Leitura e validação dos CSVs
│   ├── transform.py      ← Limpeza, tipagem e merge
│   ├── tmdb.py           ← Enriquecimento via API do TMDB
│   ├── normalize.py      ← Normalização em modelo estrela
│   └── load.py           ← Escrita dos CSVs processados / DuckDB
├── main.py               ← Entrypoint da pipeline
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

⚙️ Como Usar
1. Preparação dos Dados
Exporte seus dados do Letterboxd em: letterboxd.com/settings/data

Extraia o .zip e coloque os arquivos watched.csv, ratings.csv, diary.csv, watchlist.csv e reviews.csv na pasta data/raw/.

Obtenha uma Chave de API gratuita do TMDB em: themoviedb.org/settings/api

2. Configuração do Ambiente
Clone o repositório e configure suas credenciais:


git clone [https://github.com/seu-usuario/letterboxd-etl.git](https://github.com/seu-usuario/letterboxd-etl.git)
cd letterboxd-etl
cp .env.example .env
Abra o arquivo .env gerado e cole sua TMDB_API_KEY.

3. Execução
Opção A: Com Docker 🐳
Basta rodar o comando abaixo. O Docker vai instalar as dependências e rodar a pipeline inteira automaticamente:

docker compose up

Opção B: Sem Docker 💻
Se preferir rodar direto no Python:

pip install -r requirements.txt
python main.py
Parâmetros Extras de Execução (CLI):

python main.py --skip-tmdb : Pula a chamada do TMDB (ideal para testes locais sem API key).


💡Sobre o Cache: Os resultados da API são salvos em data/tmdb_cache.csv. Rodar a pipeline novamente só buscará filmes novos que ainda não foram cacheados, economizando tempo e requisições.

📊 Visualização no Power BI
Para facilitar, o projeto já inclui um template pronto!

Após rodar a pipeline, vá até a pasta src/BI/ e abra o arquivo etlboxd.pbit no Power BI Desktop.

Os dados serão carregados seguindo o Modelo Estrela gerado na pasta data/processed/.

O modelo conecta a tabela fato central (master.csv) com as dimensões de genres, countries, directors e actors através de tabelas ponte, gerando filtros e estatísticas personalizadas em tempo real!


🛠️ Tecnologias Utilizadas
Linguagem: Python 3.11

Processamento de Dados: Pandas

Integração: Requests (TMDB API)

Banco de Dados / Armazenamento: Arquivos CSV 

Infraestrutura: Docker 

Data Viz: Power BI Desktop
