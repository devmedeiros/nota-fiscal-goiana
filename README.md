# Nota Fiscal Goiana

## Rodando localmente

Para encriptar o nome dos vencedores também é necessário definir uma variável de ambiente: `KEY_GOIANA`.

Feito isso basta clonar o repositório

```bash
  git clone https://github.com/devmedeiros/nota-fiscal-goiana.git
```

Entre no diretório do projeto

```bash
  cd nota-fiscal-goiana
```

### Para rodar o scraper

Instale os pacotes necessários

```bash
  pip install requirements.txt
```

Rode `nfg_scrape.py` para executar o scraper da Nota Fiscal Goiana

```bash
  python src/data/nfg_scrape.py
```

Rode `arrecadacao_scrape.py` para executar o scraper da Arrecadação Estadual

```bash
  python src/data/arrecadacao_scrape.py
```

### Para rodar o Streamlit App

Rode `app.py`

```bash
  streamlit run src/visualization/app.py
```

## Stack utilizada

**Back-End:** Python (beautifulsoup, pandas, numpy, tabula-py), GitHub Actions

**DB:** SQLite

**Visualização de Dados:** Streamlit
