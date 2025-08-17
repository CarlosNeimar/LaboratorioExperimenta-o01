import requests
import pandas as pd
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN') 

headers = {
    'Authorization': f'bearer {GITHUB_TOKEN}',
    'Content-Type': 'application/json',
}

GRAPHQL_URL = 'https://api.github.com/graphql'

PAGINATED_GRAPHQL_QUERY = """
query TopStarredRepos($perPage: Int!, $cursor: String) {
  search(
    query: "stars:>=1 sort:stars-desc", 
    type: REPOSITORY, 
    first: $perPage, 
    after: $cursor
  ) {
    nodes {
      ... on Repository {
        nameWithOwner
        stargazers {
          totalCount
        }
        primaryLanguage {
          name
        }
        createdAt
        pushedAt
        pullRequests(states: MERGED) {
          totalCount
        }
        releases {
          totalCount
        }
        openIssues: issues(states: OPEN) {
          totalCount
        }
        closedIssues: issues(states: CLOSED) {
          totalCount
        }
      }
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
"""

def main():
    """Função principal para buscar e processar os dados dos repositórios via GraphQL com paginação."""
    if not GITHUB_TOKEN or GITHUB_TOKEN == 'SEU_TOKEN_AQUI':
        print("ERRO: Por favor, configure seu token de acesso pessoal do GitHub no arquivo .env.")
        return

  
    all_repos = []
    cursor = None
    repos_por_pagina = 20
    total_de_paginas = 5

    print(f"Buscando os 100 repositórios com mais estrelas ({repos_por_pagina} por página)...")

    for page_num in range(total_de_paginas):
        print(f"Buscando página {page_num + 1}/{total_de_paginas}...")

      
        variables = {
            "perPage": repos_por_pagina,
            "cursor": cursor
        }

        try:
            response = requests.post(
                GRAPHQL_URL, 
                json={'query': PAGINATED_GRAPHQL_QUERY, 'variables': variables}, 
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

            if 'errors' in data:
                print("Erro na query GraphQL:", data['errors'])
                return

            search_results = data.get('data', {}).get('search', {})
            repos_on_page = search_results.get('nodes', [])
            page_info = search_results.get('pageInfo', {})

            all_repos.extend(repos_on_page)
            
          
            cursor = page_info.get('endCursor')
            if not page_info.get('hasNextPage'):
                print("Não há mais páginas para buscar.")
                break

        except requests.exceptions.RequestException as e:
            print(f"Erro ao chamar a API GraphQL: {e}")
            return
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
            return

    if not all_repos:
        print("Nenhum repositório encontrado.")
        return
    
  
    repo_data_list = []
    print(f"\nProcessando dados para {len(all_repos)} repositórios coletados...")

    for i, repo in enumerate(all_repos):
        if not repo: 
            continue

        print(f"({i+1}/{len(all_repos)}) Processando: {repo['nameWithOwner']}")

        pushed_at = datetime.fromisoformat(repo['pushedAt'].replace('Z', '+00:00'))
        time_since_update_days = (datetime.now(timezone.utc) - pushed_at).days

        open_issues_count = repo['openIssues']['totalCount']
        closed_issues_count = repo['closedIssues']['totalCount']
        total_issues = open_issues_count + closed_issues_count
        issues_ratio_val = closed_issues_count / total_issues if total_issues > 0 else 0.0

        repo_data = {
            'Repositorio': repo['nameWithOwner'],
            'Estrelas': repo['stargazers']['totalCount'],
            'Linguagem_Primaria': repo['primaryLanguage']['name'] if repo['primaryLanguage'] else 'N/A',
            'Data_de_Criacao': repo['createdAt'].split('T')[0],
            'Dias_desde_Ultima_Atualizacao': time_since_update_days,
            'Pull_Requests_Aceitas': repo['pullRequests']['totalCount'],
            'Total_de_Releases': repo['releases']['totalCount'],
            'Razao_Issues_Fechadas_Total': f"{issues_ratio_val:.2f}"
        }
        repo_data_list.append(repo_data)

    print("\nColeta de dados finalizada.")
    
    df = pd.DataFrame(repo_data_list)
    
    csv_filename = 'top_100_github_repos_paginated_graphql.csv'
    try:
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"\nDados exportados com sucesso para o arquivo: '{csv_filename}'")
    except Exception as e:
        print(f"\nOcorreu um erro ao salvar o arquivo CSV: {e}")

    print("\n--- Amostra dos Dados Coletados ---")
    print(df.head())


if __name__ == '__main__':
    main()