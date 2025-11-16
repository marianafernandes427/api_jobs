Este projeto consiste na criação de uma Command Line Interface (CLI) em Python que permite ao utilizador interagir com a API do ITJobs.pt. 
A aplicação possibilita a consulta de ofertas de emprego, pesquisa filtrada por empresa e localidade, exportação de resultados para CSV, 
análise de skills mais frequentes e obtenção de detalhes específicos de uma vaga.
A CLI foi desenvolvida com Typer, garantindo uma interface simples e intuitiva, e utiliza bibliotecas como requests para comunicação com a API, 
csv para exportação de dados e re para análise de texto.

Estrutura do Código:

make_api_request() – Função que centraliza todos os acessos à API, permitindo requisições GET ou POST. Retorna os dados em formato JSON e trata erros de forma uniforme.
Evita repetição de código, pois cada intereção com a API exige um request. O mesmo para a variável global CONFIG. Dado que a maior parte das configurações com a API utilizam as mesmas configurações (mesmos headers, parâmetros principalmente). Também deixa o código mais limpo, cumprindo o princípio DRY e facilitando o debug.

export_to_csv() – A função export_to_csv permite exportar uma lista de ofertas de emprego para um ficheiro CSV. Após verificar se existem dados para exportar, cria o ficheiro com os campos principais (título, empresa, descrição, data, salário e localização) e escreve cada oferta linha a linha. Inclui tratamento de erros para garantir que falhas na escrita do ficheiro não interrompem o programa, informando o utilizador caso ocorra algum problema.

encontrar_work_type() – A função encontrar_work_type identifica os tipos de trabalho presentes na descrição de uma oferta. Para isso, constrói um padrão com todas as categorias definidas em WORK_TYPES e procura correspondências usando expressões regulares, sem distinguir maiúsculas de minúsculas. Devolve uma lista única dos tipos encontrados.

converter_date() - A função converter_date transforma uma data em formato de string (YYYY-MM-DD) num objeto datetime. Caso a conversão falhe, apresenta uma mensagem de erro ao utilizador e devolve None. Esta função é utilizada como apoio para validar e manipular datas em outras funções do programa.

n_jobs() – A função n_jobs obtém um número específico de ofertas de emprego a partir da API do ITJobs. Para isso, constrói um dicionário de parâmetros (incluindo limites, página e filtros adicionais), envia o pedido através da função make_api_request e devolve apenas a quantidade de resultados solicitada. Caso a API falhe ou não haja resposta, a função retorna uma lista vazia, garantindo o bom funcionamento do programa.

search_jobs() – Função que permite listar todos os trabalhos de tipo part-time por empresa e localidade, sendo possível, caso solicitado pelo usuário, exportar os dados como ficheiro csv.

retornar_p_data() - A função retornar_p_data filtra ofertas de emprego com base num intervalo de datas fornecido pelo utilizador. Primeiro converte as datas inicial e final para o formato datetime; se alguma conversão falhar, não prossegue. Em seguida, obtém a lista de empregos e compara a data de publicação de cada um, selecionando apenas os que estão dentro do intervalo definido. A função devolve a lista filtrada, ignorando automaticamente entradas com datas inválidas.

add_skills_list() - A função add_skills_list adiciona uma nova skill à lista de competências usada pelo programa. Antes de inserir, verifica se o utilizador forneceu uma skill válida e se esta já existe (comparando em minúsculas para evitar duplicados). Caso seja nova, a skill é adicionada e é apresentada uma mensagem de confirmação.

skills_muitos() – A função skills_muitos identifica e contabiliza as skills mais mencionadas nas ofertas de emprego publicadas dentro de um intervalo de datas. Primeiro obtém as ofertas filtradas através da função retornar_p_data. Depois, extrai as descrições e constrói um padrão de pesquisa que inclui todas as skills definidas na lista SKILLS_LIST. Utilizando expressões regulares, procura cada skill nas descrições, contando as ocorrências independentemente de maiúsculas/minúsculas. Por fim, organiza os resultados por ordem decrescente de frequência e devolve-os em formato JSON.

get_job_id() – A função get_job_id obtém e apresenta os detalhes completos de uma oferta de emprego com base no seu ID. Envia um pedido à API utilizando o método POST e, caso a resposta seja válida, mostra no terminal informações como título, empresa, localização, data de publicação e o URL da oferta. Além disso, analisa a descrição para identificar tipos de trabalho associados, utilizando a função encontrar_work_type. Se o ID não for encontrado, informa o utilizador.

help() - Função que permite mostrar ao utilizador os comandos disponíveis da CLI.
