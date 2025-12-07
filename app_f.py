import sys
import requests
import re
import json
from collections import Counter
from datetime import datetime
from typing import List, Optional
import typer
import csv
import requests
from bs4 import BeautifulSoup

# Variáveis Globais
# para não sobreescrever os header, chave api , link api 
CONFIGS = {
    "API_KEY": "b0e317cc2b42bdde2c5d7bdd73db79c4",
    "BASE_URL": "https://api.itjobs.pt/job",
    "SITE_URL" : "https://pt.teamlyzer.com/companies/",
    "MAX_RESULTS": 300,

    "HEADERS": {
        "User-Agent": "MyApp/1.0",
        "Accept": "application/json"
    },

    "HEADERS_SITE": {
        "User-Agent": "Mozilla/5.0 (compatible; TeamlyzerScraper/1.0)"
    }
}
def ler_html(url):
    try:
        response = requests.get(url, headers=CONFIGS["HEADERS_SITE"], timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        return soup
    except requests.RequestException as e:
        typer.echo(f"Erro {e} ao aceder a {url}")
        return None

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
        
        if not jobs:
            typer.echo("Nenhum dado para exportar.")
            return

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
        'api_key': CONFIGS["API_KEY"],
        'limit': min(num,CONFIGS['MAX_RESULTS']),
        'page': 1,
        **extras_params
    }
    response = make_api_request("list.json", params)
    return response.get("results", [])[:num] if response else []
        

def search_jobs(empresa: str, localidade: str, num: int, if_csv: bool):
    return n_jobs(
        num,
        if_csv=False,
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
    if not response or "title" not in response:
        typer.echo(f"Não foi possível encontrar detalhes para o job ID {job_id}.")
        return

    typer.echo(f"Título: {response.get('title', 'N/A')}")
    typer.echo(f"Empresa: {response.get('company', {}).get('name', 'N/A')}")
    typer.echo(f"Localização: {response.get('locations', [{}])[0].get('name', 'N/A')}")
    typer.echo(f"Data: {response.get('publishedAt', 'N/A')}")
    typer.echo(f"URL: https://www.itjobs.pt/job/{response.get('id', job_id)}")

    tipos = encontrar_work_type(response.get("description", ""))
    typer.echo("Tipos de trabalho: " + ", ".join(tipos) if tipos else "Nenhum tipo encontrado.")
    return response

   
def info_empresa(res):
    if res: 
        nome_empresa = res["company"]["name"]
        nome_empresa_formatada = nome_empresa.replace(" ", "-").lower()
        link = CONFIGS["SITE_URL"] + nome_empresa_formatada + "/benefits-and-values"
        soup = ler_html(link)
        
        if not soup:
            typer.echo(f"Não foi possível acessar a página: {link}")
            return
        
        # rating
        ranking_element = soup.find(class_="text-center aa_rating")
        # em princípio funciona , pk está nessa classe em várias empresas
        if ranking_element:
            ranking = ranking_element.get_text(strip=True)
            typer.echo(f"Rating da empresa: {ranking}")
        else:
            # outro local para rating
            rating_selectors = [".aa_rating", ".rating", "[class*='rating']", ".text-center"]
            for selector in rating_selectors:
                rating_elem = soup.select_one(selector)
                if rating_elem:
                    ranking = rating_elem.get_text(strip=True)
                    typer.echo(f"Rating da empresa: {ranking}")
                    break
            else:
                typer.echo("Rating não encontrado")
        
        # encontrar descrição
        descricao_element = soup.find(class_="ellipsis center_mobile")
        if descricao_element:
            descricao = descricao_element.get_text(strip=True)
            typer.echo(f"Descrição da empresa {nome_empresa}: {descricao}")
        else:
            # outras secções possíveis
            desc_selectors = [".ellipsis", ".center_mobile", ".company-description", ".about-company"]
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    descricao = desc_elem.get_text(strip=True)
                    typer.echo(f"Descrição da empresa {nome_empresa}: {descricao}")
                    break
            else:
                typer.echo("Descrição não encontrada")
        
        typer.echo("\nBenefícios:")
        beneficios_encontrados = False
        beneficios_elements = soup.find_all(class_="text-mute1")
        
        if not beneficios_elements:
            values_lists = soup.find_all(class_="values_list")
            for values_list in values_lists:
                beneficios_elements.extend(values_list.find_all(class_="text-mute1"))
        
        # local esperado dos beneficios
        if not beneficios_elements:
            titulos_beneficios = soup.find_all(class_="flex_details")
            for titulo in titulos_beneficios:
                typer.echo(f"- {titulo.get_text(strip=True)}")
                beneficios_encontrados = True
        
        # procesar elementos
        if beneficios_elements:
            for elem in beneficios_elements:
                texto = elem.get_text(strip=True)
                if texto: 
                    typer.echo(f"- {texto}")
                    beneficios_encontrados = True
        
        # procurar possíveis candidatos para buscar info
        if not beneficios_encontrados:
            # procurar outras secççoes
            benefit_sections = soup.find_all(class_=lambda x: x and "benefit" in x.lower() if x else False)
            
            for section in benefit_sections:
                paragraphs = section.find_all(["p", "li", "div"])
                for p in paragraphs:
                    texto = p.get_text(strip=True)
                    if texto and len(texto) > 15: 
                        typer.echo(f"- {texto}")
                        beneficios_encontrados = True
        
        if not beneficios_encontrados:
            typer.echo(f"Não foram encontrados benefícios específicos para {nome_empresa}")
            
            # Debug (retirar dps)
            typer.echo("\n[DEBUG] Estrutura da página encontrada:")
            typer.echo(f"Título da página: {soup.title.string if soup.title else 'Sem título'}")
            
            # Mostrar algumas das soluções possíveis
            classes_encontradas = set()
            for tag in soup.find_all(class_=True):
                classes = tag.get("class", [])
                classes_encontradas.update(classes)
            
            typer.echo(f"Classes CSS encontradas (total: {len(classes_encontradas)}):")
            for classe in sorted(list(classes_encontradas))[:15]: 
                typer.echo(f"  • {classe}")
                
                   
# Montar CLI

@app.command()
def list_jobs(num: int, csv: bool = typer.Option(False, "--csv", help="Exportar resultados para CSV")):
    #Listar N jobs ou exportar para CSV
    jobs = n_jobs(num, if_csv=csv)
    if csv:
        export_to_csv(jobs, "jobs_export.csv")
    else:
        typer.echo(json.dumps(jobs, ensure_ascii=False, indent=2))

@app.command()
def search(empresa: str, localidade: str, num: int, csv: bool = typer.Option(False, "--csv")):
    # Listar trabalhos part-time por empresa e localidade
    jobs = search_jobs(empresa, localidade, num, if_csv=csv)
    if csv:
        export_to_csv(jobs, "search_export.csv")
    else:
        typer.echo(json.dumps(jobs, ensure_ascii=False, indent=2))
@app.command()
def job(job_id: int):
    # Obter detalhes de um job específico por id
    res = get_job_id(job_id)
    if res:
        info_empresa(res)

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