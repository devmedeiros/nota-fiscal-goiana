# Carregando pacotes para Scrap inicial
from bs4 import BeautifulSoup
import requests
import pandas as pd
import tabula as tb
import re

url = 'https://www.economia.go.gov.br/sorteios/index.php?option=com_content&view=article&layout=edit&id=7388'
page = requests.get(url)

soup = BeautifulSoup(page.text, features="lxml")

table = soup.find('table')
sorteios = pd.read_html(str(table))[0]
new_header = sorteios.iloc[0]
sorteios = sorteios[1:]
sorteios.columns = new_header

# Configurando os links dos resultados
url_base = 'https://www.economia.go.gov.br'

url_resultados = []
j = 0
for i in table.find_all('a'):
    j += 1
    if j%2 == 0:
        if i['href'][0] == 'h':
            url_resultados.append(i['href'])
        else:
            url_resultados.append(url_base+i['href'])

sorteios['links'] = url_resultados

# Links dos PDFs
url_pdf = []
for link in sorteios.links:
    page = requests.get(link)
    soup = BeautifulSoup(page.text, features="lxml")
    url_ = soup.find('a', attrs={'class': 'btn btn-success'})['href']
    if url_[0] == 'h':
        url_pdf.append(url_)
    else:
        url_pdf.append(url_base+url_)

sorteios['url_pdf'] = url_pdf

# Organizando as colunas
sorteios.columns = ['n_sorteio', 'realizacao', 'url_resultado', 'url_pdf']

# Formatando n_sorteio para ter apenas 2 dígitos
for i in sorteios.index:
    sorteios.loc[i, 'n_sorteio'] = sorteios.loc[i, 'n_sorteio'][:2]

# Conectando no BD
from dotenv import load_dotenv
load_dotenv()

modules = dir()

print(modules)
print(os.environ)

import os
from sqlalchemy import create_engine

args = {
            'user': os.getenv("USERNAME"),
            'password': os.getenv("PASSWORD"),
            'host': os.getenv("HOST"),
            'database': os.getenv("DATABASE"),
            'ssl': {'ca': 'cacert.pem'}
        }

engine = create_engine('mysql+pymysql://{user}:{pass}@{host}/{db}', connect_args=args)

# Se o scrap trouxe dados novos, adiciona
sorteios_ = pd.read_sql('SELECT n_sorteio FROM sorteios', con=engine)

sorteios = sorteios[~sorteios.n_sorteio.isin(sorteios_.n_sorteio)]

sorteios.to_sql(name='sorteios', con=engine, index=False, if_exists='append')

# Definindo função de ler os PDFs
import numpy as np

def read_pdfs(file):
    try:
        data = tb.read_pdf(file, pages = 'all', pandas_options={'header': None})
    except:
        data = tb.read_pdf(file, pages = 'all', pandas_options={'header': None}, stream=True)
        if not (data[0].shape[1] == data[1].shape[1] == data[2].shape[1]):
            data[0] = data[0][data[0].columns[data[0].isnull().mean() < 0.9]]
            data[0].columns = range(len(data[0].columns))

            data[1] = data[1][data[1].columns[data[1].isnull().mean() < 0.9]]
            data[1].columns = range(len(data[1].columns))

            data[2] = data[2][data[2].columns[data[2].isnull().mean() < 0.9]]
            data[2].columns = range(len(data[2].columns))
    data = pd.concat([data[0],data[1],data[2]])
    return data

dicionario = {
    'No Prêmio': 'n_premio',
    'No Bilhete': 'n_bilhete',
    'Nome': 'nome',
    'Valor Prêmio*': 'valor_premio',
    'Município': 'municipio',
    'UF': 'uf',
    'No': 'n_premio',
    'No Sorteio': 'n_sorteio',
    'No Premio': 'n_premio',
    'Prêmio': 'n_premio'
}

# Definindo função de tratar as tabelas dos PDFs
def trataTabela(temp, sorteio):
    new_header = temp.iloc[0]
    temp = temp[1:]
    temp.columns = new_header
    temp.rename(columns=dicionario, inplace=True)

    if temp.columns.isna().sum() == 1:
        if not ('municipio' in temp.columns):
            temp.columns = temp.columns.fillna('municipio')
        elif not ('nome' in temp.columns):
            temp.columns = temp.columns.fillna('nome')
        elif not ('valor_premio' in temp.columns):
            temp.columns = temp.columns.fillna('valor_premio')
    else:
        temp.columns.values[int(np.where(temp.columns == 'n_bilhete')[0])+1] = 'nome'
        temp.columns.values[int(np.where(temp.columns == 'nome')[0])+1] = 'municipio'
    if not ('n_sorteio' in temp.columns):
        temp['n_sorteio'] = str(sorteio)
    temp.n_sorteio = temp.n_sorteio.astype(str).str.strip()
    if not ('uf' in temp.columns):
        temp['uf'] = np.nan
    return temp

# Tratamento dos dados
resultados = pd.DataFrame()
for index in sorteios.index:
    temp = read_pdfs(sorteios.loc[index, 'url_pdf'])
    temp = trataTabela(temp, sorteios.loc[index, 'n_sorteio'])
    resultados = pd.concat([resultados, temp])

resultados = resultados.loc[:,['n_sorteio', 'n_premio', 'n_bilhete', 'nome', 'municipio', 'uf', 'valor_premio']]
resultados.reset_index(drop=True, inplace=True)

for i in resultados[resultados.valor_premio.isna()].index:
    resultados.loc[i, 'valor_premio'] = re.findall(r'[\d.,]+', 'GOIAS 1.000,00')[0]
    resultados.loc[i, 'uf'] = re.sub(r'[\d.,]+', '', 'GOIAS 1.000,00').strip()

# Criptografando os nomes
from cryptography.fernet import Fernet
import os

KEY_GOIANA = os.environ.get('KEY_GOIANA')

fernet = Fernet(KEY_GOIANA)

resultados['nome_encriptado'] = np.nan
for index in resultados.index:
    resultados.loc[index, 'nome_encriptado'] = fernet.encrypt(resultados.loc[index, 'nome'].encode()).decode('utf-8')

resultados.drop(columns='nome', inplace=True)

# Recuperando UFs
municipios = pd.read_csv('dados/municipios.csv')

dicionario_municipios = dict(zip(municipios.nome_simples, municipios.uf_simples))

resultados.municipio = resultados.municipio.str.strip()

mun_dict = {
    'JARDIM ABC DE GOIAS': 'CIDADE OCIDENTAL',
    'DOMICIANO RIBEIRO': 'CRISTALINA',
    'CLAUDINAPOLIS': 'NAZARIO',
    'GOIAPORA': 'AMORINOPOLIS'
}

resultados.municipio.replace(mun_dict, inplace=True)

resultados.uf.fillna(resultados.municipio.map(dicionario_municipios), inplace=True)

# Afirmando tipos
dresultados = {
    'n_sorteio': 'int64',
    'n_premio': 'int64',
    'n_bilhete': 'object',
    'municipio': 'object',
    'uf': 'object',
    'valor_premio': 'float',
    'nome_encriptado': 'object'
    
}

resultados.astype(dresultados)

# Salvando os resultados no BD
from sqlalchemy import Integer, String, Numeric
dtypes = {
    'n_sorteio': Integer,
    'n_premio': Integer,
    'n_bilhete': String(200),
    'municipio': String(200),
    'uf': String(200),
    'valor_premio': Numeric,
    'nome_encriptado': String(200)
    
}

resultados.to_sql(name = 'resultados', con=engine, index=False, if_exists='append', dtype=dtypes)