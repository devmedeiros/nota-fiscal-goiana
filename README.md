# Nota Fiscal Goiana
<p align="center"><img src="https://img.shields.io/badge/status-development-2ea44f" alt="status - development"></p>

Este projeto faz a coleta dos resultados do programa Nota Fiscal Goiana, trata os dados e os salva em um banco de dados online MySQL. Além disso os dados são apresentados num _dashboard_ de Power BI.

Como o sorteio é feito mensalmente, o scrap dos dados é feito apenas uma vez ao mês alguns dias após sair os resultados, sem aumento no tráfego do site.

Para conhecer mais sobre o programa visite o [site oficial](https://www.economia.go.gov.br/institucional-nf.html).

## Como funciona essa projeto?

Esse projeto executa um processo ETL (_Extract, Transform, and Load_), a extração é feita através do Python usando técnicas de _web-scraping_ e antes de salvar no banco é verificado se a informação encontrada é nova, se for salva o primeiro _data frame_ **sorteios** no banco. Após isso é necessário encontrar os vencedores do sorteio, cada sorteio tem seu resultado divulgado no Diário da União e no próprio site do programa é anexado um PDF, neste projeto é extraído os vencedores lendo o PDF e transformando suas informações para um formato mais legível e completo. Quando o segundo e último _data frame_ está no formato correto ele é acrescentado ao banco de dados, agora numa tabela chamada **resultados**.

O script python foi salvo no arquivo `main.py` e está agendado para rodar no dia 5 de todos os meses pelo Github Actions, o banco de dados é MySQL e está disponível online, então o Github Actions consegue executar o pipeline de ETL sem a necessidade de intervenção humana.

Um relatório interativo de Power BI exibindo os dados coletados está disponível aqui. Abaixo possui um diagrama exemplificando o pipeline de dados.

![projeto nf-go](https://user-images.githubusercontent.com/33239902/196008245-a83172ba-9b4b-467a-93e8-66bd4880e009.png)

## Stack utilizada

**Back-End:** Python (beautifulsoup, pandas, numpy, tabula-py)

**DB:** MySQL

**Visualização de Dados:** Power BI
