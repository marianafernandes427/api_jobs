import sys
import requests
import re
import json
from collections import Counter
from datetime import datetime
import typer
import csv


app = typer.Typer(help="CLI de ITjobs")
# auxiliares
def export_to_csv(jobs: list, filename: str):

    fieldnames = ["titulo", "empresa", "descricao", "data_publicacao", "salario", "localizacao"]

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
    typer.echo(f"Empregos exportados para {filename}")
    
skills_list = [
        'Python', 'JavaScript', 'Java', 'C#', 'C++', 'PHP', 'Ruby', 'Go', 'Swift', 'Kotlin',
        'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
        'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring', 'Laravel',
        'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Linux', 'Git', 'Jenkins',
        'Machine Learning', 'AI', 'Data Science', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy',
        'HTML', 'CSS', 'SASS', 'TypeScript', 'REST', 'GraphQL', 'API',
        'Agile', 'Scrum', 'DevOps', 'CI/CD', 'TDD', 'Microservices'
    ]

work_types = [
    "remoto",
    "hibrido",
    "presencial",
    "outro",
    "full_time",
    "part_time",
    "freelancer",
    "contrato_a_termo",
    "outsourcing",
    "on_site_cliente",
    "nearshore",
    "offshore",
    "projeto_pontual",
    "estagio_trainee",
    "on_call_piquete"
]

def encontrar_work_type(descricao):
    padrao = r'\b(?:' + '|'.join(re.escape(t) for t in work_types) + r')\b'
    matches = re.findall(padrao, descricao, flags=re.IGNORECASE)
    return list(set([m.lower() for m in matches]))

chave_api = "b0e317cc2b42bdde2c5d7bdd73db79c4"
api_url = "https://www.itjobs.pt/api"
# fim

def n_jobs(num: int, if_csv: bool):
    headers = {
        'User-Agent': 'MyApp/1.0',
        'Accept': 'application/json'
    }
    
    params = {
        'api_key': chave_api,
        'limit': num,
        'page': 1
    }
    try:
        response = requests.get(
            'https://api.itjobs.pt/job/list.json',
            params=params,
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json() # converter json
            jobs = data.get('results', [])[:num]

            if not if_csv:
                return jobs
            else:
                export_to_csv(jobs, "jobs_export.csv")
                return []

        else:
            return []
    except Exception as e:
        typer.echo(f"Erro {e} ao tentar fazer o request")
        
def search_jobs(empresa: str, localidade: str, num: int, if_csv: bool):
    headers = {
        'User-Agent': 'MyApp/1.0',
        'Accept': 'application/json'
    }
    params = {
        'api_key': chave_api,
        'limit': num,
        'page': 1,
        'company': empresa,
        'location': localidade,
        'type': 'part-time'
    }
    try:
        response = requests.get('https://api.itjobs.pt/job/list.json', params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('results', [])[:num]
            if not if_csv:
                return jobs
            else:
                export_to_csv(jobs, "search_export.csv")
                return []
        else:
            return []
    except Exception as e:
        typer.echo(f"Erro {e} ao tentar fazer o request")
        return []

def add_skills_list(skill: str):
    if not skill:
        typer.echo("Nenhuma skill foi introduzida como argumento. Forneça uma skill")
        return
    if skill.lower() in [s.lower() for s in skills_list]:
        typer.echo("Essa skill já existe na lista de skills")
        return
    else:
        skills_list.append(skill)
        typer.echo(f"Skill {skill} adicionada com sucesso à lista de skills")
        return skills_list
    
def retornar_por_data(data_inicial: str, data_final: str):
    # pedir json
    # retornar por data
    # converter strings para datetime
    data_i = datetime.strptime(data_inicial, "%Y-%m-%d")
    data_f = datetime.strptime(data_final, "%Y-%m-%d")

    headers = {
        'User-Agent': 'MyApp/1.0',
        'Accept': 'application/json'
    }

    # vamos buscar mais vagas 
    params = {
        'api_key': chave_api,
        'limit': 300,
        'page': 1
    }

    try:
        response = requests.get(
            'https://api.itjobs.pt/job/list.json',
            params=params,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        jobs = data.get('results', [])

        # filtrar por datas
        filtrados = []
        for job in jobs:
            try:
                d = datetime.strptime(job["publishedAt"][:10], "%Y-%m-%d")
                if data_i <= d <= data_f:
                    filtrados.append(job)
            except:
                continue

        return filtrados

    except requests.exceptions.RequestException as e:
        typer.echo(f"Erro ao fazer request à API: {e}")
        return []


def skills_muitos(data_inicial_skills, data_final_skills):
    # ordenar por data
    por_data = retornar_por_data(data_inicial_skills, data_final_skills)
    
    if not por_data:
        typer.echo("Não existem dados para fazer a contagem das skills")
        return json.dumps([])
    # filtrar descrições
    descricoes = [item.get('description', '') for item in por_data if item.get('description')]
    # ordenar
    skills_ordenadas = sorted(skills_list, key=lambda x: len(x.split()), reverse=True)
    #escrever padrao
    padrao = r'\b(?:' + '|'.join(re.escape(s) for s in skills_ordenadas) + r')\b'
    
    counter = Counter()
    # loop para procurar todoas as skills 
    for descricao in descricoes:
        matches = re.findall(padrao, descricao, flags=re.IGNORECASE)
        for match in matches:
            skill_original = next((s for s in skills_list if s.lower() == match.lower()), match)
            # contagem
            counter[skill_original] += 1

    resultado_final = dict(sorted(counter.items(), key=lambda item: item[1], reverse=True))

    return json.dumps([resultado_final], ensure_ascii=False, indent=2)
# nenhuma das palavras da skill list precisa de escrita em ascci



def get_job_id(job_id: int):
    url = "https://api.itjobs.pt/job/get.json"
    # precisa de ter mais detalhes para user agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }    
    data = {"api_key": chave_api, "id": job_id}
    
    response = requests.post(url, data=data, headers=headers)
    
    if response.status_code == 200:
        vaga = response.json()
        typer.echo(f"{vaga['title']}")
        typer.echo(f"{vaga['company']['name']}")
        typer.echo(f"{vaga['locations'][0]['name']}")
        typer.echo(f"{vaga['publishedAt']}")
        typer.echo(f"https://www.itjobs.pt/job/{vaga['id']}")
        
        descricao = vaga.get("description", "")
        encontrados = encontrar_work_type(descricao)
        if encontrados:
            typer.echo(f"Tipo(s) de trabalho(s) em {job_id}: {', '.join(encontrados)}")
        else:
             typer.echo(f"Nenhum tipo de trabalho encontrado na descrição da vaga {job_id} .")

    else:
        typer.echo(f"Erro {response.status_code}")
        
def help():
    typer.echo("""
Comandos disponíveis:
  add_skill <nome_skill>         - Adicionar skills para procurar posteriormente
  skills <skills>         - Mostra os trabalhos com essa skill
  get_job <int_job>        - Mostra as característica de um trabalho num índice específico
  Exit                 - Sair do programa
  Help                - Mostra os comandos disponíveis
""")

# Montar CLI

@app.command()
def list_jobs(num: int, csv: bool = typer.Option(False, "--csv", help="Exportar resultados para CSV")):
    """Listar N jobs ou exportar para CSV"""
    n_jobs(num, csv)

@app.command()
def search(empresa: str, localidade: str, num: int, csv: bool = typer.Option(False, "--csv", help="Exportar resultados para CSV")):
    """Listar trabalhos part-time por empresa e localidade"""
    search_jobs(empresa, localidade, num, csv)

@app.command()
def add_skill(skill: str):
    """Adicionar uma nova skill à lista"""
    add_skills_list(skill)

@app.command()
def job(job_id: int):
    """Obter detalhes de um job específico"""
    get_job_id(job_id)

@app.command()
def skills(data_inicial: str, data_final: str):
    """Contar skills mais frequentes entre duas datas (YYYY-MM-DD)"""
    print(skills_muitos(data_inicial, data_final))

@app.command()
def help():
    help()
if __name__ == "__main__":
    app()
