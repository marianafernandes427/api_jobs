import sys
import requests
import re
import json
from collections import Counter
from datetime import datetime
import typer

skills_list = [
        'Python', 'JavaScript', 'Java', 'C#', 'C++', 'PHP', 'Ruby', 'Go', 'Swift', 'Kotlin',
        'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
        'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring', 'Laravel',
        'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Linux', 'Git', 'Jenkins',
        'Machine Learning', 'AI', 'Data Science', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy',
        'HTML', 'CSS', 'SASS', 'TypeScript', 'REST', 'GraphQL', 'API',
        'Agile', 'Scrum', 'DevOps', 'CI/CD', 'TDD', 'Microservices'
    ]

chave_api = "b0e317cc2b42bdde2c5d7bdd73db79c4"
api_url = "https://www.itjobs.pt/api"

# adicionar comando para poder adicionar mais skills 

def add_skills_list(skill):
    if skill.strip().lower() not in skills_list.lower():
        skills_list.append(skill)
        return skills_list
    
def retornar_por_data(data_inicial, data_final):
    # pedir json
    # obter parâmetros
    try:
        headers = {
    'User-Agent': 'MyApp/1.0',           
    'Accept': 'application/json' } 
        # Diferentes formas de passar parâmetros de data para a API
        params = {
            'start_date': data_inicial,
            'end_date': data_final,
            'api_key': chave_api
        }
        
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer request à API: {e}")
        return []
    
def skills(data_inicial_skills, data_final_skills):
    # obter requests por data primeiro
    por_data = retornar_por_data(data_inicial_skills, data_final_skills)
    
    # apenas filtrar em descrições
    so_descricao = []
    if not por_data:
        print("Não existem dados para fazer a contagem das skills")
        return json.dumps([])
    
    for item in por_data:
        descricao = item.get('description')
        if descricao:
            so_descricao.append(descricao)
    
    # criar regex para todas as skills
    padrao = r'\b(?:' + '|'.join(re.escape(s) for s in skills_list) + r')\b'    
    counter = Counter()
    
    for descricao in so_descricao:
        # encontra todas as ocorrências da lista de skills
        matches = re.findall(padrao, descricao, flags=re.IGNORECASE) # usar findall para várias palavras
        for match in matches:
            # incrementar contador mantendo o case original da skill na lista
            # se quiser unificar maiúsculas/minúsculas, usar match.lower()
            counter[match] += 1
    resultado_final = dict(sorted(counter.items(), key=lambda item: item[1], reverse=True))
    # ordem decrescente
    return json.dumps([resultado_final], ensure_ascii= False, indent=2)
"""Versão multipalavra"""    

def skills_multipalavra(data_inicial_skills, data_final_skills):
    por_data = retornar_por_data(data_inicial_skills, data_final_skills)
    
    if not por_data:
        print("Não existem dados para fazer a contagem das skills")
        return json.dumps([])
    
    # Extrair todas as descrições
    descricoes = [item.get('description', '') for item in por_data if item.get('description')]
    
    # Ordena skills multipalavra primeiro para evitar sobreposição
    skills_ordenadas = sorted(skills_list, key=lambda x: len(x.split()), reverse=True)
    
    # Criar regex único que case todas as skills (multipalavra e simples)
    padrao = r'\b(?:' + '|'.join(re.escape(s) for s in skills_ordenadas) + r')\b'
    
    counter = Counter()
    
    for descricao in descricoes:
        matches = re.findall(padrao, descricao, flags=re.IGNORECASE)
        for match in matches:
            # Incrementa contador mantendo case original da skill
            # Podemos mapear match para a skill original para unificar maiúsculas/minúsculas
            skill_original = next((s for s in skills_list if s.lower() == match.lower()), match)
            counter[skill_original] += 1
    resultado_final = dict(sorted(counter.items(), key=lambda item: item[1], reverse=True))
    # Retorna ordenado por ocorrências decrescentes
    return json.dumps([resultado_final], ensure_ascii= False, indent=2) 
# nenhuma das palavras da skill list precisa de escrita em ascci



def get_job(job_id):
    url = "https://api.itjobs.pt/job/get.json"
    
    headers = {
        # precisa de ter mais detalhes para user agent
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }    
    data = {"api_key": chave_api, "id": job_id}
    
    response = requests.post(url, data=data, headers=headers)
    
    if response.status_code == 200:
        vaga = response.json()
        print(f"{vaga['title']}")
        print(f"{vaga['company']['name']}")
        print(f"{vaga['locations'][0]['name']}")
        print(f"{vaga['publishedAt']}")
        print(f"https://www.itjobs.pt/job/{vaga['id']}")
    else:
        print(f"Erro {response.status_code}")

print(get_job(506525))
