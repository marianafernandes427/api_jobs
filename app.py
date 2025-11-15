import sys
import requests
import re
import json
from collections import Counter
from datetime import datetime
from typing import List, Optional
import typer
import csv

# Variáveis Globais
# para não sobreescrever os header, chave api , link api 
CONFIGS = {
    'HEADERS': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    },
    'API_KEY': "b0e317cc2b42bdde2c5d7bdd73db79c4",
    'BASE_URL': "https://api.itjobs.pt/job",
    'MAX_RESULTS': 300
}

app = typer.Typer(help="CLI de ITjobs")
# auxiliares
# para nao escrever sempre os requests
def make_api_request(endpoint: str, params: dict, method: str = 'GET') -> Optional[dict]:
    url = f"{CONFIGS['BASE_URL']}/{endpoint}"
    # para método get e post
    try:
        if method.upper() == 'GET':
            response = requests.get(url, params=params, headers=CONFIGS['HEADERS'], timeout=15)
        else:
            response = requests.post(url, data=params, headers=CONFIGS['HEADERS'], timeout=15)
        
        response.raise_for_status()
        return response.json() # já converte para json todos os requests
    
    except requests.exceptions.RequestException as e:
        typer.echo(f"Erro {e} na API, não foi possível realizar o request", err=True)
        return None
    
def export_to_csv(jobs: list, filename: str):
    if not jobs:
        typer.echo("Não exite nenhum trabalho para exportar para CSV")
        return
    
    fieldnames = ["titulo", "empresa", "descricao", "data_publicacao", "salario", "localizacao"]
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for job in jobs:
                row = {
                    "titulo": job.get("title", ""),
                    "empresa": job.get("company", {}).get("name", ""),
                    "descricao": job.get("description", ""),
                    "data_publicacao": job.get("publishedAt", ""),
                    "salario": job.get("wage", ""),
                    "localizacao": ", ".join([loc.get("name", "") for loc in job.get("locations", [])])
                }
                writer.writerow(row)
        typer.echo(f"Empregos exportados para ficheiro {filename}")
    except Exception as e:
        typer.echo(f"Erro {e} ao tentar exportar para csv", err=True)

# fazer procuras    
SKILLS_LIST = [
        'Python', 'JavaScript', 'Java', 'C#', 'C++', 'PHP', 'Ruby', 'Go', 'Swift', 'Kotlin',
        'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
        'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring', 'Laravel',
        'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Linux', 'Git', 'Jenkins',
        'Machine Learning', 'AI', 'Data Science', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy',
        'HTML', 'CSS', 'SASS', 'TypeScript', 'REST', 'GraphQL', 'API',
        'Agile', 'Scrum', 'DevOps', 'CI/CD', 'TDD', 'Microservices'
              ]

WORK_TYPES = ["remoto","hibrido","presencial","outro","full_time","part_time","freelancer","contrato_a_termo",
    "outsourcing","on_site_cliente","nearshore","offshore","projeto_pontual","estagio_trainee","on_call_piquete"
             ]    
# fim fazer procuras

def encontrar_work_type(descricao):
    if not descricao:
        return
    
    padrao = r'\b(?:' + '|'.join(re.escape(t) for t in WORK_TYPES) + r')\b'
    matches = re.findall(padrao, descricao, flags=re.IGNORECASE)
    return list(set([m.lower() for m in matches]))

def converter_date(date_formato_string : str) -> Optional[datetime]:
    try:
        return datetime.strptime(date_formato_string, "%Y-%m-%d")
    except Exception as e:
        typer.echo(f"Erro {e} ao tentar converter {date_formato_string} para tipo datetime.")
        typer.echo(f"Não retornará nada")
        return None
# fim funções auxiliares

def n_jobs(num: int, if_csv: bool, **extras_params): # extra paramns faz dicionário
    params = {
        'api_key': CONFIGS["CHAVE_API"],
        'limit': min(num,CONFIGS['MAX_RESULTS']),
        'page': 1
        **extras_params
    }
    response = make_api_request("list.json", params)
    return response.get("results", [])[:num] if response else []
        
def search_jobs(empresa: str, localidade: str, num: int):
    """Pesquisa jobs por empresa e localidade"""
    return search_jobs(
        num,
        company=empresa,
        location=localidade,
        type="part-time"
    )

def retornar_p_data(data_inicial: str, data_final:str):
    dinicial = converter_date(data_inicial)
    dfinal = converter_date(data_final)
    if not dinicial or dfinal:
        typer.echo("Uma das datas não foi convertida.")
        typer.echo("Nada será retornado")
        return []
    jobs = search_jobs(CONFIGS["MAX_RESULTS"])
    filtrados = []

    for job in jobs:
        try:
            d = datetime.strptime(job["publishedAt"][:10], "%Y-%m-%d")
            if dinicial <= d <= dfinal:
                filtrados.append(job)
        except:
            continue
    return filtrados

    
def add_skills_list(skill: str):
    if not skill:
        typer.echo("Nenhuma skill foi introduzida como argumento. Forneça uma skill")
        return
    if skill.lower() in [s.lower() for s in SKILLS_LIST]:
        typer.echo("Essa skill já existe na lista de skills")
        return
    else:
        SKILLS_LIST.append(skill)
        typer.echo(f"Skill {skill} adicionada com sucesso à lista de skills")
        return SKILLS_LIST
  

def skills_muitos(data_inicial_skills, data_final_skills):
    jobs = retornar_p_data(data_inicial_skills, data_final_skills)
    if not jobs:
        return json.dumps([])
    # filtrar campo descrições
    descricoes = [j.get("description", "") for j in jobs]
    # ordenar
    skills_ordenadas = sorted(SKILLS_LIST, key=lambda x: len(x.split()), reverse=True)
    #escrever padrao
    padrao = r'\b(?:' + '|'.join(re.escape(s) for s in skills_ordenadas) + r')\b'
    
    counter = Counter()
    # loop para procurar todoas as skills 
    for descricao in descricoes:
        matches = re.findall(padrao, descricao, flags=re.IGNORECASE)
        for match in matches:
            skill_original = next((s for s in SKILLS_LIST if s.lower() == match.lower()), match)
            # contagem
            counter[skill_original] += 1

    resultado_final = dict(sorted(counter.items(), key=lambda item: item[1], reverse=True))

    return json.dumps([resultado_final], ensure_ascii=False, indent=2)
# nenhuma das palavras da skill list precisa de escrita em ascci


# info de job id específico
def get_job_id(job_id: int):
    
    infos = {"api_key": CONFIGS["API_KEY"], "id": job_id}
    response = make_api_request("get.json", infos, method="POST")
    if not response:
        typer.echo(f"Job com id {job_id} não encontrado")
        return
    typer.echo(f"{response['title']}")
    typer.echo(f"{response['company']['name']}")
    typer.echo(f"{response['locations'][0]['name']}")
    typer.echo(f"{response['publishedAt']}")
    typer.echo(f"https://www.itjobs.pt/job/{response['id']}")
     
     # mostrar os tipos de trabalho da vaga
    tipos = encontrar_work_type(response.get("description", ""))
    typer.echo("Tipos de trabalho: " + ", ".join(tipos) if tipos else "Nenhum tipo encontrado.")
    

# Montar CLI

@app.command()
def list_jobs(num: int, csv: bool = typer.Option(False, "--csv", help="Exportar resultados para CSV")):
    #Listar N jobs ou exportar para CSV
    jobs = n_jobs(num)
    if csv:
        export_to_csv(jobs)
    else:
        typer.echo(json.dumps(jobs, ensure_ascii=False, indent=2))

@app.command()
def search(empresa: str, localidade: str, num: int, csv: bool = typer.Option(False, "--csv")):
    # Listar trabalhos part-time por empresa e localidade
    jobs = search_jobs(empresa, localidade, num)
    if csv:
        export_to_csv(jobs, "search_export.csv")
    else:
        typer.echo(json.dumps(jobs, ensure_ascii=False, indent=2))
@app.command()
def add_skill(skill: str):
    # Adicionar uma nova skill à lista
    add_skills_list(skill)

@app.command()
def job(job_id: int):
    # Obter detalhes de um job específico por id
    get_job_id(job_id)

@app.command()
def skills(data_inicial: str, data_final: str):
    # Contar skills mais frequentes entre duas datas
    print(skills_muitos(data_inicial, data_final))

@app.command()
def add_skill(skill : str):
    if not skill.strip():
        typer.echo("Nenhuma skill fornecida.")
        typer.echo("Nada adicionado à lista de skills")
        return
    if skill.lower() in [s.lower() for s in SKILLS_LIST]:
        typer.echo("A skill já existe na lista.")
        return
    SKILLS_LIST.append(skill)
    typer.echo(f"Skill '{skill}' adicionada com sucesso à lista de skills.")
    

@app.command()
def help():
    typer.echo("""
Comandos disponíveis:

 top N [--csv]                  - Listar N jobs mais recentes.
 search EMPRESA LOCAL N [--csv] - Listar jobs part-time por empresa e localidade.
 type JOBID                     - Extrair tipo de trabalho de um job.
 skills DATA_INICIAL DATA_FINAL - Contar skills entre datas.
 add_skill [skill]              - Adiciona uma skill à lista de skills           
""")
    
if __name__ == "__main__":
    app()