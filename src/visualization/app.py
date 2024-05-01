"""
Comentários
"""
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import datetime
import plotly.express as px
import locale

# Definindo configurações da página
st.set_page_config(
        page_title="Nota Fiscal Goiana",
        page_icon="🌽",
        layout="wide",
        menu_items={
        'Report a bug': 'https://github.com/devmedeiros/nota-fiscal-goiana/issues/new',
        'About': '''Desenvolvido e mantido por [Jaqueline Medeiros](http://devmedeiros.com/pt/about/). O código fonte e os dados podem ser acessados no ![github-logo](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWdpdGh1YiI+PHBhdGggZD0iTTE1IDIydi00YTQuOCA0LjggMCAwIDAtMS0zLjVjMyAwIDYtMiA2LTUuNS4wOC0xLjI1LS4yNy0yLjQ4LTEtMy41LjI4LTEuMTUuMjgtMi4zNSAwLTMuNSAwIDAtMSAwLTMgMS41LTIuNjQtLjUtNS4zNi0uNS04IDBDNiAyIDUgMiA1IDJjLS4zIDEuMTUtLjMgMi4zNSAwIDMuNUE1LjQwMyA1LjQwMyAwIDAgMCA0IDljMCAzLjUgMyA1LjUgNiA1LjUtLjM5LjQ5LS42OCAxLjA1LS44NSAxLjY1LS4xNy42LS4yMiAxLjIzLS4xNSAxLjg1djQiLz48cGF0aCBkPSJNOSAxOGMtNC41MSAyLTUtMi03LTIiLz48L3N2Zz4=) 
    [repositório](https://github.com/devmedeiros/nota-fiscal-goiana/).'''
    }
    )

# Criando a conexão dos dados
engine = create_engine('sqlite:///database/nf-goiana.db')

# ------------------------------------------------------------------------------------------------------------
# Definindo a barra lateral
# ------------------------------------------------------------------------------------------------------------

# Carregando os filtros
opcoes_uf = pd.read_sql('select distinct m.uf_nome from municipios m inner join resultados r on m.nome_simples = r.municipio and r.uf = m.uf_simples order by 1', con=engine)
opcoes_municipios = pd.read_sql('select distinct m.municipio from municipios m inner join resultados r on m.nome_simples = r.municipio and r.uf = m.uf_simples order by 1', con=engine)

with st.sidebar:
    st.title('Filtros')

    selecao_uf = st.multiselect('Unidade Federativa', opcoes_uf, placeholder='Escolha uma opção')
    selecao_municipio = st.multiselect('Município', opcoes_municipios, placeholder='Escolha uma opção')

    st.markdown('---')

    st.markdown('''Desenvolvido e mantido por [Jaqueline Medeiros](http://devmedeiros.com/pt/about/). O código fonte e os dados podem ser acessados no ![github-logo](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWdpdGh1YiI+PHBhdGggZD0iTTE1IDIydi00YTQuOCA0LjggMCAwIDAtMS0zLjVjMyAwIDYtMiA2LTUuNS4wOC0xLjI1LS4yNy0yLjQ4LTEtMy41LjI4LTEuMTUuMjgtMi4zNSAwLTMuNSAwIDAtMSAwLTMgMS41LTIuNjQtLjUtNS4zNi0uNS04IDBDNiAyIDUgMiA1IDJjLS4zIDEuMTUtLjMgMi4zNSAwIDMuNUE1LjQwMyA1LjQwMyAwIDAgMCA0IDljMCAzLjUgMyA1LjUgNiA1LjUtLjM5LjQ5LS42OCAxLjA1LS44NSAxLjY1LS4xNy42LS4yMiAxLjIzLS4xNSAxLjg1djQiLz48cGF0aCBkPSJNOSAxOGMtNC41MSAyLTUtMi03LTIiLz48L3N2Zz4=) 
    [repositório](https://github.com/devmedeiros/nota-fiscal-goiana/).''')

# ------------------------------------------------------------------------------------------------------------
# Definindo o corpo principal
# ------------------------------------------------------------------------------------------------------------

sorteios = pd.read_sql('select n_sorteio, realizacao from sorteios', con=engine)

# Filtro UF
if len(selecao_uf) == 0:
    segmentacao_uf = str(tuple([str(i) for i in opcoes_uf['uf_nome']]))
elif len(selecao_uf) == 1:
    segmentacao_uf = f"('{selecao_uf[0]}')"
else:
    segmentacao_uf = str(tuple([str(i) for i in selecao_uf]))

# Filtro Município
if len(selecao_municipio) == 0:
    segmentacao_municipio = str(tuple([str(i) for i in opcoes_municipios['municipio']]))
elif len(selecao_municipio) == 1:
    segmentacao_municipio = f"('{selecao_municipio[0]}')"
else:
    segmentacao_municipio = str(tuple([str(i) for i in selecao_municipio]))

resultados_query = f"""
select 
	coalesce(m.municipio, '-') municipio,
	coalesce(m.uf_nome, '-') uf,
	sum(r.valor_premio) soma_premio, 
	round(avg(r.valor_premio), 2) media_premio, 
	count(1) qtde_premio, 
	latitude, 
	longitude 
from 
	resultados r
	left join municipios m on m.nome_simples = r.municipio and r.uf = m.uf_simples
where
    m.uf_nome in {segmentacao_uf}
    and m.municipio in {segmentacao_municipio}
group by 
	1,2,6,7
order by 
	count(1) desc"""
resultados = pd.read_sql(resultados_query, con=engine)

arrecadacao_query = """
select
    data_arrecadacao,
    "total",
    round(((b.total_y - a."total")/b.total_y)*100,2) variacao,
    1 color
from
    arrecadacao a
    left join (select date(data_arrecadacao, '-1 month') data_ante, "total" total_y from arrecadacao) b on b.data_ante = a.data_arrecadacao
where
    data_arrecadacao > '2010-01-01';
"""
arrecadacao = pd.read_sql(arrecadacao_query, con=engine, parse_dates={"data_arrecadacao": {'format': '%Y-%m-%d'}})

# ------------------------------------------------------------------------------------------------------------
# Definindo o corpo principal
# ------------------------------------------------------------------------------------------------------------

st.title('Acompanhamento dos Sorteios')

# ------------------------------------------------------------------------------------------------------------
# Criando indicadores básicos
col1, col2, col3 = st.columns(3)
col1.metric("Sorteios Acompanhados", f'{len(sorteios.n_sorteio)}/{max(sorteios.n_sorteio)}')
col2.metric("Último Sorteio", f'{max(sorteios.realizacao)}')
col3.metric("Total Sorteado", f'R$ {sum(resultados.soma_premio):,}'.replace(',','.'))

st.markdown('---')

# ------------------------------------------------------------------------------------------------------------

# Dicionário para renomear colunas
config_dict = {
    'uf': 'UF',
    'municipio': 'Município',
    'media_premio': 'Média dos Prêmios',
    'soma_premio': 'Soma dos Prêmios',
    'qtde_premio': 'Qtde Prêmios'}

# Resumo da distribuição do sorteio
with st.container():
    col1, col2 = st.columns([2, 1])
    resultados_ = resultados.iloc[:,:5].style.format(precision=2, thousands='.',decimal=',')
    col1.dataframe(data=resultados_, hide_index=True, column_config=config_dict, use_container_width=True, height=400)
    p1 = px.scatter_mapbox(resultados[~resultados.latitude.isnull()], lat='latitude', lon='longitude', hover_name="municipio",
     hover_data=['uf', 'soma_premio', 'media_premio', 'qtde_premio'], zoom=3, color_discrete_sequence=['#FCC016'], height=400)
    p1.update_layout(mapbox_style="open-street-map")
    p1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    col2.plotly_chart(p1, use_container_width=True, theme=None)

# ------------------------------------------------------------------------------------------------------------
# Arrecadação do ICMS
st.subheader('Arrecadação do ICMS no Período')
p2 = px.area(arrecadacao, x='data_arrecadacao', y='total', color='color', color_discrete_map={1: '#FCC016'}, template='plotly_white', labels={'data_arrecadacao': 'Período', 'total': 'Total Arrecadado'})
p2.update_layout(showlegend=False, plot_bgcolor='white')
p2.add_vline(x=datetime.datetime.strptime("2011-01-01", "%Y-%m-%d").timestamp() * 1000, annotation_text="Início Comparação", line_width=3, line_dash="dash", line_color="green")
p2.add_vline(x=datetime.datetime.strptime("2015-01-01", "%Y-%m-%d").timestamp() * 1000, annotation_text="Início Programa", line_width=3, line_dash="dash", line_color="green")
p2.add_vline(x=datetime.datetime.strptime("2019-01-01", "%Y-%m-%d").timestamp() * 1000, annotation_text="Pausa Programa", line_width=3, line_dash="dash", line_color="green")
p2.add_vline(x=datetime.datetime.strptime("2021-01-01", "%Y-%m-%d").timestamp() * 1000, annotation_text="Retomada Programa", line_width=3, line_dash="dash", line_color="green")
st.plotly_chart(p2, use_container_width=True, theme=None)

# ------------------------------------------------------------------------------------------------------------
# Definindo datas
inicio_comparacao = datetime.datetime(2011, 1, 1)
inicio_programa = datetime.datetime(2015, 1, 1)
pausa_programa = datetime.datetime(2019, 1, 1)
retomada_programa = datetime.datetime(2021, 1, 1)

# calculando o período
ante_programa = arrecadacao[(arrecadacao.data_arrecadacao >= inicio_comparacao) & (arrecadacao.data_arrecadacao < inicio_programa)]
dps_programa = arrecadacao[(arrecadacao.data_arrecadacao >= inicio_programa) & (arrecadacao.data_arrecadacao < pausa_programa)]
ante_pausa = arrecadacao[(arrecadacao.data_arrecadacao >= pausa_programa) & (arrecadacao.data_arrecadacao < retomada_programa)]
dps_pausa = arrecadacao[(arrecadacao.data_arrecadacao >= retomada_programa) & (arrecadacao.data_arrecadacao < datetime.datetime.now())]

st.markdown('---')

# criação das medidas
st.subheader('Variação Média')
col1, col2, col3, col4 = st.columns(4)
col1.metric("Antes do programa", f'{round(ante_programa.variacao.mean(),2):.2n}')
col2.metric("Após o ínicio do programa", f'{round(dps_programa.variacao.mean(),2):.2n}')
col3.metric("Início da pausa", f'{round(ante_pausa.variacao.mean(),2):.2n}')
col4.metric("Após a pausa", f'{round(dps_pausa.variacao.mean(),2):.2n}')