import requests
import pandas as pd
from datetime import datetime

GITHUB_TOKEN = ' Insira o token '
API_URL = 'https://api.github.com/graphql'
HEADERS = {
    'Authorization': f'bearer {GITHUB_TOKEN}',
}

# Na consulta GraphQL, configurei para buscar apenas 1 repositório por página. 
# Quando tenei valores maiores, a api do github apresentou erro de timeout.
query_consolidada = """
  query TopStarredRepositories($cursor: String) {
    search(
      query: "stars:>1"
      type: REPOSITORY
      first: 1
      after: $cursor
    ) {
      pageInfo {
        endCursor
        hasNextPage
      }
      nodes {
        ... on Repository {
          nameWithOwner
          stargazers {
            totalCount
          }
          createdAt
          pushedAt
          primaryLanguage {
            name
          }
          releases {
            totalCount
          }
          pullRequests(states: MERGED) {
            totalCount
          }
          issues_total: issues {
            totalCount
          }
          issues_closed: issues(states: CLOSED) {
            totalCount
          }
        }
      }
    }
  }
"""


def main():
    """Função principal para coletar e salvar os dados."""
    todos_repos = []
    cursor = None
    num_pag = 0
    
    print("Iniciando a coleta de dados dos 1000 repositórios mais populares...")

    # A paginação buscará 10 páginas de 100 repositórios cada.
    while len(todos_repos) < 1000:
        num_pag += 1
        add_vars = {'cursor': cursor}

        try:
            result = exec_query_graphql(query_consolidada, add_vars)
            data = result.get('data', {}).get('search', {})
            repos = data.get('nodes', [])
            
            for repo in repos:
                # Evita adicionar repositórios sem dados
                if not repo:
                    continue

                lang = repo.get('primaryLanguage')
                todos_repos.append({
                    'repository': repo.get('nameWithOwner'),
                    'stars': repo.get('stargazers', {}).get('totalCount'),
                    'creation_date': repo.get('createdAt'),
                    'last_update_date': repo.get('pushedAt'),
                    'primary_language': lang['name'] if lang else 'N/A',
                    'total_releases': repo.get('releases', {}).get('totalCount'),
                    'accepted_pull_requests': repo.get('pullRequests', {}).get('totalCount'),
                    'total_issues': repo.get('issues_total', {}).get('totalCount'),
                    'closed_issues': repo.get('issues_closed', {}).get('totalCount'),
                })

            page_info = data.get('pageInfo', {})
            cursor = page_info.get('endCursor')
            has_next_page = page_info.get('hasNextPage')

            print(f"Página {num_pag} coletada. Total de repositórios: {len(todos_repos)}")

            if not has_next_page:
                print("Não há mais páginas para buscar.")
                break
        
        except requests.exceptions.HTTPError as err:
            print(f"Erro na requisição: {err}")
            print(f"Resposta da API: {err.response.text}")
            break
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
            break

    rel_csv = gera_relatorio_csv(todos_repos, 'repositorios_populares.csv')

    if rel_csv is None:
        print("Arquivo CSV não foi gerado devido a falta de dados.")
        return
    
    print(f"Total de {len(rel_csv)} repositórios foram salvos em 'repositorios_populares.csv'.")
    print("\nVisualização das primeiras linhas do arquivo csv:")
    print(rel_csv.head())


def exec_query_graphql(query, variables):
    response = requests.post(API_URL, json={'query': query, 'variables': variables}, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def gera_relatorio_csv(result_graphql, nome_arquivo):    
    
    df = pd.DataFrame(result_graphql)

    if df.empty:
        print("\nDataframe vazio, arquivo csv não será gerado.")
        return
    
    # Convertendo as datas para datetime
    df['creation_date'] = pd.to_datetime(df['creation_date'])
    df['last_update_date'] = pd.to_datetime(df['last_update_date'])

    # Calculando idade do repositório
    df['repository_age_days'] = (datetime.now().astimezone() - df['creation_date']).dt.days

    # Calculando tempo desde a última atualização
    df['days_since_last_update'] = (datetime.now().astimezone() - df['last_update_date']).dt.days

    # Calculando razão de issues fechadas
    df['closed_issues_ratio'] = df.apply(
        lambda row: row['closed_issues'] / row['total_issues'] if row['total_issues'] > 0 else 0,
        axis=1
    )
    
    df.to_csv(nome_arquivo, index=False)
    return df


if __name__ == '__main__':
    main()