# Carregando pacotes para Scrap das Arrecadações
import pandas as pd
from sqlalchemy import create_engine
from bs4 import BeautifulSoup
import requests
from datetime import date, datetime
import os
import re
import locale
from config import BASE_DIR
from db import get_engine

locale.setlocale(locale.LC_ALL, 'pt_PT.UTF-8')

# Criando engine
engine = get_engine()

url = 'https://dadosabertos.go.gov.br/dataset/arrecadacao'
page = requests.get(url)

soup = BeautifulSoup(page.text, features="lxml")

# Configurando os links dos resultados
url_base = 'https://dadosabertos.go.gov.br'

# Links dos csvs
links = []
titulos = []
for link in soup.find_all('a'):
    if link.find('span', {'data-format': 'csv'}):
        links.append(url_base + link.get('href'))
        titulos.append(link.get('title'))

# Checando dados que já foram coletados
padrao = r'\b\w+/\d{4}\b'
datas = [datetime.strptime(re.search(padrao, string)[0], '%B/%Y').strftime('%Y-%m-%d') for string in titulos if re.search(padrao, string)]
temp = pd.DataFrame({'data_arrecadacao': datas, 'links': links})
arrecadacao_ = pd.read_sql("select data_arrecadacao from arrecadacao", con=engine)
temp = temp[~temp['data_arrecadacao'].isin(arrecadacao_['data_arrecadacao'])]

# Função para acessar a página que estão os CSVs e pegar o URL de download
def downloadCSV(url):
    inner_page = requests.get(url)
    inner_soup = BeautifulSoup(inner_page.text, features="lxml")
    unique_links = set()
    for link in inner_soup.find_all('a'):
        href = link.get('href')
        if href and href.endswith('.csv') and href not in unique_links:
            unique_links.add(href)
    if len(unique_links) == 1:
        return list(unique_links)[0]
    else:
        raise Exception("Mais de um link de download encontrado, verificar página.")

# Lendo dados novos
if not temp.empty:
    arrecadacao = pd.DataFrame()
    for arquivo in temp.links:
        temp = pd.read_csv(downloadCSV(arquivo), sep=';')
        arrecadacao = pd.concat([arrecadacao, temp[temp['TIPO_RECEITA'] == 'ICMS']])

    # Formatando as informações
    arrecadacao.reset_index(drop=True, inplace=True)

    arrecadacao['ano'] = [int(str(x)[:4]) for x in arrecadacao['ANO_MES']]
    arrecadacao['mes'] = [int(str(x)[-2:]) for x in arrecadacao['ANO_MES']]
    arrecadacao['total'] = [pd.to_numeric(x.replace(',', '.')) for x in arrecadacao['VALR_TOTAL']]
    arrecadacao['data_arrecadacao'] = [date(year=arrecadacao.ano[i], month=arrecadacao.mes[i], day=1) for i in arrecadacao.index]

    arrecadacao = arrecadacao[['data_arrecadacao', 'total']]

    # Salvando as informações novas
    arrecadacao.to_sql(name = 'arrecadacao', con=engine, index=False, if_exists='append')
else:
    print('Nenhuma informação nova encontrada')