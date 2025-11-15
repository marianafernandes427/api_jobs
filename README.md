Este projeto consiste na criação de uma Command Line Interface (CLI) em Python que permite ao utilizador interagir com a API do ITJobs.pt. 
A aplicação possibilita a consulta de ofertas de emprego, pesquisa filtrada por empresa e localidade, exportação de resultados para CSV, 
análise de skills mais frequentes e obtenção de detalhes específicos de uma vaga.
A CLI foi desenvolvida com Typer, garantindo uma interface simples e intuitiva, e utiliza bibliotecas como requests para comunicação com a API, 
csv para exportação de dados e re para análise de texto.

Estrutura do Código:
make_api_request() – Função genérica para chamadas à API.
n_jobs() – Lista vagas.
search_jobs() – Pesquisa por filtros.
export_to_csv() – Exporta resultados para CSV.
skills_muitos() – Conta skills mais frequentes.
get_job_id() – Detalhes de uma vaga.
converter_date() – Conversão de datas.
encontrar_work_type() – Identificação do tipo de trabalho.
