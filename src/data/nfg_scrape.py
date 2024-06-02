# Carregando pacotes para Scrap inicial
from bs4 import BeautifulSoup
import requests
import re
import os
import pandas as pd
import tabula as tb
import numpy as np
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import Integer, String, Numeric
from cryptography.fernet import Fernet
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from datetime import datetime

# Carregando variáveis de ambiente
load_dotenv()

# Definindo caminhos
caminho_script = os.path.dirname(os.path.abspath(__file__))
caminho_db = os.path.abspath(os.path.join(caminho_script, '../../database/nf-goiana.db'))

url = 'https://goias.gov.br/nfgoiana/numero-dos-sorteios/'

# Configurações do navegador
options = webdriver.FirefoxOptions()
options.add_argument("-headless")
options.set_preference('browser.download.folderList', 2)
options.set_preference('browser.download.dir', caminho_script)
options.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/pdf')
options.set_preference("browser.download.manager.showWhenStarting", False)
options.set_preference("pdfjs.disabled", True)
browser = webdriver.Firefox(options=options)

browser.get(url)

soup = BeautifulSoup(browser.page_source, 'html.parser')

table = soup.find('table')
sorteios = pd.read_html(str(table))[0]
new_header = sorteios.iloc[0]
sorteios = sorteios[1:]
sorteios.columns = new_header

# Configurando os links dos resultados
url_base = 'https://goias.gov.br'

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

# Organizando as colunas
sorteios.columns = ['n_sorteio', 'realizacao', 'url_resultado']

sorteios['n_sorteio'] = sorteios.n_sorteio.str.split('/')
sorteios = sorteios.explode('n_sorteio')

# Criando conexão com o database
engine = create_engine(f'sqlite:///{caminho_db}')

# Se o scrap trouxe dados novos, adiciona
sorteios_ = pd.read_sql('select n_sorteio from sorteios', con=engine)
sorteios_lista = [str(a) for a in sorteios_.n_sorteio]
sorteios = sorteios[~sorteios.n_sorteio.isin(sorteios_lista)]

# Links dos PDFs
url_pdf = []
for link in sorteios.url_resultado:
    browser.get(link)
    time.sleep(5)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    for a in soup.findAll('a', href=True): #Encontra todos os links da página que possuem href
        if '.pdf' in a['href']: #Se o link conter .pdf
            url_ = a['href'] #Salva como url do resultado
    if url_[0] == 'h':
        url_pdf.append(url_)
    else:
        url_pdf.append(url_base+url_)

sorteios['url_pdf'] = url_pdf

# Formatando realizacao
sorteios['realizacao'] = [datetime.strptime(x, "%d/%m/%Y").strftime("%Y-%m-%d") for x in sorteios.realizacao]

# Afirmando tipo dos sorteios
dsorteios = {
        'n_sorteio': 'int64',
        'realizacao': 'object',
        'url_resultado': 'object',
        'url_pdf': 'object'
    }

sorteios = sorteios.astype(dsorteios)

if not sorteios.empty:
    # Salvando sorteios no banco de dados
    sorteios[['n_sorteio','realizacao']].to_sql(name='sorteios', con=engine, index=False, if_exists='append')

    # Definindo função de ler os PDFs
    def read_pdfs(file):
        try:
            data = tb.read_pdf(file, pages = 'all', pandas_options={'header': None}) # Tenta ler o PDF sem especificar o cabeçalho
        except:
            data = tb.read_pdf(file, pages = 'all', pandas_options={'header': None}, stream=True) # Se houver erro, tenta ler o PDF em modo de stream
            if not (data[0].shape[1] == data[1].shape[1] == data[2].shape[1]):# Verifica se as dimensões dos DataFrames extraídos são diferentes
                # Filtra colunas com mais de 90% de valores nulos e renomeia as colunas
                data[0] = data[0][data[0].columns[data[0].isnull().mean() < 0.9]]
                data[0].columns = range(len(data[0].columns))

                data[1] = data[1][data[1].columns[data[1].isnull().mean() < 0.9]]
                data[1].columns = range(len(data[1].columns))

                data[2] = data[2][data[2].columns[data[2].isnull().mean() < 0.9]]
                data[2].columns = range(len(data[2].columns))
        data = pd.concat([data[0],data[1],data[2]])
        os.remove(file)
        print('Arquivo removido')
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
        'Prêmio': 'n_premio',
        'Prêmio*': 'valor_premio'
    }

    # Definindo função de tratar as tabelas dos PDFs
    def trataTabela(temp, sorteio):
        new_header = temp.iloc[0]
        temp = temp[1:]
        temp.columns = new_header
        temp.rename(columns=dicionario, inplace=True)

        # Verifica se há apenas uma coluna com valor NaN
        if temp.columns.isna().sum() == 1:
            # Se 'municipio' não estiver presente, preenche a coluna NaN com 'municipio'
            if not ('municipio' in temp.columns):
                temp.columns = temp.columns.fillna('municipio')
            # Se 'nome' não estiver presente, preenche a coluna NaN com 'nome'
            elif not ('nome' in temp.columns):
                temp.columns = temp.columns.fillna('nome')
            # Se 'valor_premio' não estiver presente, preenche a coluna NaN com 'valor_premio'
            elif not ('valor_premio' in temp.columns):
                temp.columns = temp.columns.fillna('valor_premio')
        else:
            temp.columns.values[int(np.where(temp.columns == 'n_bilhete')[0])+1] = 'nome' # Renomeia a coluna após 'n_bilhete' como 'nome'
            temp.columns.values[int(np.where(temp.columns == 'nome')[0])+1] = 'municipio' # Renomeia a coluna após 'nome' como 'municipio'
        # Se 'n_sorteio' não estiver presente, cria uma coluna 'n_sorteio' e atribui o valor de 'sorteio'
        if not ('n_sorteio' in temp.columns):
            temp['n_sorteio'] = str(sorteio)
        temp.n_sorteio = temp.n_sorteio.astype(str).str.strip() # Remove espaços em branco da coluna 'n_sorteio'
        # Se 'uf' não estiver presente, cria uma coluna 'uf' com valores NaN
        if not ('uf' in temp.columns):
            temp['uf'] = np.nan
        return temp

    def downloadPDF(url):
        try:
            browser.get(url)
        except:
            for i in os.listdir(caminho_script):
                if i.lower().endswith('.pdf'):
                    print('Arquivo baixado')
                    pdf_path = caminho_script+'/'+i
                    return pdf_path
            sys.exit(1)

    # Define um timeout de 5 segundos
    browser.set_page_load_timeout(5)

    # Tratamento dos dados
    resultados = pd.DataFrame()
    for index in sorteios.index:
        pdf_path = downloadPDF(sorteios.loc[index, 'url_pdf'])
        temp = read_pdfs(pdf_path)
        temp = trataTabela(temp, sorteios.loc[index, 'n_sorteio'])
        resultados = pd.concat([resultados, temp])

    resultados = resultados.loc[:,['n_sorteio', 'n_premio', 'n_bilhete', 'nome', 'municipio', 'uf', 'valor_premio']]
    resultados.reset_index(drop=True, inplace=True)

    for i in resultados[resultados.valor_premio.isna()].index:
        resultados.loc[i, 'valor_premio'] = re.findall(r'[\d.,]+', 'GOIAS 1.000,00')[0]
        resultados.loc[i, 'uf'] = re.sub(r'[\d.,]+', '', 'GOIAS 1.000,00').strip()

    # Criptografando os nomes
    KEY_GOIANA = os.environ.get('KEY_GOIANA')

    fernet = Fernet(KEY_GOIANA)

    resultados['nome_encriptado'] = np.nan
    for index in resultados.index:
        resultados.loc[index, 'nome_encriptado'] = fernet.encrypt(resultados.loc[index, 'nome'].encode()).decode('utf-8')

    resultados.drop(columns='nome', inplace=True)

    # Recuperando UFs
    municipios = pd.read_sql('select nome_simples, uf_simples from municipios', con=engine)

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

    # Corrigindo o formato do valor do prêmio
    resultados.valor_premio = resultados.valor_premio.str.replace(',00', '', regex=True).str.replace('.', '', regex=True)

    resultados = resultados.astype(dresultados)

    # Salvando os resultados no BD
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

else:
    print("Nenhum resultado novo encontrado")