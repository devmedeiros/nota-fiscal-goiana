# Carregando pacotes para Scrap das Arrecadações
import pandas as pd
from sqlalchemy import create_engine
from bs4 import BeautifulSoup
import requests

engine = create_engine('sqlite:///dados/nf-goiana.db')

url = 'http://www.transparencia.go.gov.br/dadosabertos/index.php?dir=arrecadacao%2F'
page = requests.get(url)

soup = BeautifulSoup(page.text, features="lxml")

# Configurando os links dos resultados
url_base = 'http://www.transparencia.go.gov.br/dadosabertos/'

# Links dos csvs
links = []
for link in soup.find_all('a'):
    if link.get('href').endswith('.csv'):
        links.append(url_base + link.get('href'))

# Checando dados que já foram coletados
anomes = [str(x[-10:][:6]) for x in links]
temp = pd.DataFrame({'anomes': anomes, 'links': links})
arrecadacao_ = pd.read_sql("select ano||substr('0'||mes, -2) as anomes from arrecadacao", con=engine)
temp[~temp['anomes'].isin(arrecadacao_['anomes'])]

# Lendo dados novos
if not temp.empty:
    arrecadacao = pd.DataFrame()
    for arquivo in temp.links:
        temp = pd.read_csv(arquivo, sep=';')
        arrecadacao = pd.concat([arrecadacao, temp[temp['TIPO_RECEITA'] == 'ICMS']])

    # Formatando as informações
    arrecadacao['ano'] = [int(str(x)[:4]) for x in arrecadacao['ANO_MES']]
    arrecadacao['mes'] = [int(str(x)[-2:]) for x in arrecadacao['ANO_MES']]
    arrecadacao['total'] = [pd.to_numeric(x.replace(',', '.')) for x in arrecadacao['VALR_TOTAL']]

    arrecadacao.reset_index(drop=True, inplace=True)

    arrecadacao = arrecadacao[['ano', 'mes', 'total']]

    # Salvando as informações novas
    arrecadacao.to_sql(name = 'arrecadacao', con=engine, index=False, if_exists='append')
else:
    print('Nenhuma informação nova encontrada')