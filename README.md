# Nota Fiscal Goiana
<p align="center"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="license - mit"> <img src="https://img.shields.io/badge/Status-Development-2ea44f" alt="status - development"> <a href="https://github.com/devmedeiros/nota-fiscal-goiana/actions/workflows/scrape.yml"><img src="https://github.com/devmedeiros/nota-fiscal-goiana/actions/workflows/scrape.yml/badge.svg"></a> </p>

Este projeto faz a coleta dos resultados do programa Nota Fiscal Goiana, trata os dados e os salva em um banco de dados online MySQL. Além disso os dados são apresentados num _dashboard_ de Power BI.

Como o sorteio é feito mensalmente, o scrap dos dados é feito apenas uma vez ao mês alguns dias após sair os resultados, sem aumento no tráfego do site.

Para conhecer mais sobre o programa visite o [site oficial](https://www.economia.go.gov.br/institucional-nf.html).

## Como funciona essa projeto?

Esse projeto   executa um processo ETL (_Extract, Transform, and Load_), a extração é feita através do Python usando técnicas de _web-scraping_ e antes de salvar no banco é verificado se a informação encontrada é nova e se for, salva o primeiro _data frame_ **sorteios** no banco. Após isso é necessário encontrar os vencedores do sorteio, cada sorteio tem seu resultado divulgado no Diário da União e no próprio site do programa é anexado um PDF, neste projeto é extraído os vencedores lendo o PDF e transformando suas informações para um formato mais legível e completo. Quando o segundo e último _data frame_ está no formato correto ele é acrescentado ao banco de dados, agora numa tabela chamada **resultados**.

![diagrama relacional](https://user-images.githubusercontent.com/33239902/197660147-b6df90ba-c1b0-41b0-9e1a-92a419e6a25b.png)

O script python foi salvo no arquivo `main.py` e está agendado para rodar no dia 5 de todos os meses pelo Github Actions, o banco de dados é MySQL e está disponível online, assim o Github Actions consegue executar o processo de ETL sem a necessidade de intervenção humana.

Um relatório interativo de Power BI exibindo os dados coletados está disponível [aqui](https://app.powerbi.com/view?r=eyJrIjoiOTEyNTkyYjgtOTk2OS00NWNiLThmNzMtZGQ3MjBjYzM4YTA2IiwidCI6ImIxY2E3YTgxLWFiZjgtNDJlNS05OGM2LWYyZjJhOTMwYmEzNiJ9). Abaixo possui a arquitetura do projeto.

![diagrama projeto](https://user-images.githubusercontent.com/33239902/197660134-750effed-85af-4231-a765-48148a9eb0b5.png)

## Rodando localmente

Para rodar o projeto com um banco MySQL é necessário definir algumas variáveis de ambiente no seu .env: `DATABASE`, `HOST`, `PASSWORD`, e `USERNAME`

Para encriptar e decriptar o nome dos vencedores também é necessário definir uma variável no seu ambiente: `KEY_GOIANA`.

Feito isso basta clonar o repositório

```bash
  git clone https://github.com/devmedeiros/nota-fiscal-goiana.git
```

Entre no diretório do projeto

```bash
  cd nota-fiscal-goiana
```

Instale os pacotes necessários

```bash
  pip install requirements.txt
```

Rode `main.py`

```bash
  python main.py
```

## Stack utilizada

**Back-End:** Python (beautifulsoup, pandas, numpy, tabula-py)

**DB:** MySQL

**Visualização de Dados:** Power BI
