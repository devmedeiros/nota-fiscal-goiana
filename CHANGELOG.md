2024-06-02  Jaqueline Medeiros  <jaqueline@devmedeiros.com>

    Reescrevendo o nfg_scrape.py para encontrar o link do PDF usando um método mais genérico.

    * Modificado nfg_scrape.py
    * Modificado scrape.yml para rodar também quando houver push na branch main

2024-05-01  Jaqueline Medeiros  <jaqueline@devmedeiros.com>

    Reescrevendo o nfg_scrape.py para se adequar ao novo layout do portal da Nota Fiscal Goiana, aproveitando para organizar o banco nf-goiana e salvar os dados no formato correto.

	* Modificado nf-goiana.db adicionando constraints, removendo colunas obsoletas e corrigindo formato de dados
    * Modificado app.py para adequar as mudanças do banco de dados e corrigir formatação dos dados
    * Modificado nfg_scrape.py para adequar ao novo layout do site e melhorando a forma de salvar os dados

2024-04-04  Jaqueline Medeiros  <jaqueline@devmedeiros.com>

    Reescrevendo o nfg_scrape.py para utilizar Selenium e aplicado uma correção que diminui as requisições no portal da Nota Fiscal Goiana.

	* Modificado nfg_scrape.py
    * Modificado scrape.yml

2024-03-11  Jaqueline Medeiros  <jaqueline@devmedeiros.com>

    Criando Changelog, aposentando o Power Bi, e apresentando o Streamlit

	* Adicionado CHANGELOG.md
    * Removido sorteio.pbix
    * Adicionado relatório dos dados em Streamlit src/visualization/app.py

2024-03-10  Jaqueline Medeiros  <jaqueline@devmedeiros.com>

    Corrigindo extração da Arrecadação

	* Adicionado localização de português no scrape.yml 
    * Modificado arrecadacao.py

2023-10-01  Jaqueline Medeiros  <jaqueline@devmedeiros.com>

    Corrigindo diretório e conexões com o banco

	* Modificado nfg_scrape.py
    * Modificado arrecadacao.py

2023-09-02  Jaqueline Medeiros  <jaqueline@devmedeiros.com>

    Reorganizando repositório e acrescentando nova licença

	* Modificado LICENSE.md 
    * Modificado main.py >> nfg_scrape.py renomeando arquivo para maior claridade
    * Modificado README.md

2023-07-02  Jaqueline Medeiros  <jaqueline@devmedeiros.com>

	* Adicionado default.css resizing dinâmico

2023-07-01  Jaqueline Medeiros  <jaqueline@devmedeiros.com>

    Nova branch gh-pages

	* Adicionado index.html código html da página com a visualização de Power BI embutida

2023-06-13  Jaqueline Medeiros  <jaqueline@devmedeiros.com>

    Reorganizando repositório, nova extração e atualização dos requirements

	* Modificado requirements.txt 
    * Adicionado arrecadacao.py com código de web scraping da Arrecadação de Goiás
    * Modificado main.py correções de erros

2023-05-29  Jaqueline Medeiros  <jaqueline@devmedeiros.com>

	* Modificado scrape.yml trocando conexão do banco de dados do MySQL para SQLite e colocando commit

2023-05-07  Jaqueline Medeiros  <jaqueline@devmedeiros.com>

	* Modificado sorteio.pbix

2022-12-01  Jaqueline Medeiros  <jaqueline@devmedeiros.com>

	* Modificado main.py para conter uma condição que verifica se houve coleta de dados novos

2022-11-04  Jaqueline Medeiros  <jaqueline@devmedeiros.com>

	* Modificado scrape.yml mudando cron de "0 0 5 * *" para "0 0 1 * *"

2022-10-28  Jaqueline Medeiros  <jaqueline@devmedeiros.com>

	* Corrigido main.py pequenos bugs e quebras de extração
    * Modificado main.py trocando o banco de dados para MySQL

2022-10-17  Jaqueline Medeiros  <jaqueline@devmedeiros.com>

	Configurando o Github Actions

	* Adicionado scrape.yml
    * Modificado main.py trocando o banco de dados para MySQL

2022-10-15  Jaqueline Medeiros  <jaqueline@devmedeiros.com>

	* Adicionado README.md
    * Adicionado comentários nos códigos
    * Modificado sorteio.pbix

2022-10-12  Jaqueline Medeiros  <jaqueline@devmedeiros.com>

    Primeiro commit: Definindo estrutura inicial do projeto

    * Adicionado main.py com código de web scraping da Nota Fiscal Goiana
    * Adicionado requirements.txt para dependencias de Python
    * Adicionado sorteio.pbix
    * Adicionado municipios.ipynb
    * Adicionado pasta Dados com nf-goiana.db e municipios.csv