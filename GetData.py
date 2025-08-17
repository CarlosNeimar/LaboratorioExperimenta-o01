import requests
import pandas as pd
from datetime import datetime, timezone
import os
import time
import random
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN') 

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'Python-GitHub-Analytics/1.0'
}

# URLs da API REST do GitHub
SEARCH_URL = 'https://api.github.com/search/repositories'
REPO_BASE_URL = 'https://api.github.com/repos'

def fazer_requisicao_com_retry(url, params=None, max_tentativas=5, delay_inicial=1):
    """
    Faz uma requisição REST com retry automático em caso de erros temporários.
    """
    for tentativa in range(max_tentativas):
        try:
            print(f"  Tentativa {tentativa + 1}/{max_tentativas}...")
            
            response = requests.get(
                url, 
                headers=headers,
                params=params,
                timeout=30
            )
            
            # Verifica rate limit nos headers
            rate_limit_remaining = response.headers.get('X-RateLimit-Remaining')
            rate_limit_reset = response.headers.get('X-RateLimit-Reset')
            
            if rate_limit_remaining:
                print(f"  Rate limit restante: {rate_limit_remaining}")
                
                if int(rate_limit_remaining) < 10:
                    reset_time = datetime.fromtimestamp(int(rate_limit_reset))
                    print(f"  Rate limit baixo. Reset em: {reset_time}")
                    
                    # Se o rate limit está muito baixo, espera
                    if int(rate_limit_remaining) < 5:
                        wait_time = int(rate_limit_reset) - int(time.time()) + 5
                        if wait_time > 0:
                            print(f"  Aguardando reset do rate limit ({wait_time} segundos)...")
                            time.sleep(wait_time)
            
            # Verifica se a resposta foi bem-sucedida
            if response.status_code == 200:
                return response.json()
            
            # Rate limit excedido
            elif response.status_code == 403 and 'rate limit' in response.text.lower():
                print(f"  Rate limit excedido. Aguardando reset...")
                if rate_limit_reset:
                    wait_time = int(rate_limit_reset) - int(time.time()) + 5
                    if wait_time > 0:
                        time.sleep(wait_time)
                continue
            
            # Para erros 5xx (servidor), tenta novamente
            elif 500 <= response.status_code < 600:
                print(f"  Erro do servidor ({response.status_code}): {response.reason}")
                if tentativa < max_tentativas - 1:
                    delay = delay_inicial * (2 ** tentativa) + random.uniform(0, 1)
                    print(f"  Aguardando {delay:.1f} segundos antes de tentar novamente...")
                    time.sleep(delay)
                    continue
                else:
                    print("  Número máximo de tentativas excedido.")
                    return None
            
            # Para outros erros HTTP
            else:
                print(f"  Erro HTTP ({response.status_code}): {response.reason}")
                if response.status_code == 422:  # Unprocessable Entity
                    print(f"  Detalhes: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"  Timeout na tentativa {tentativa + 1}")
            if tentativa < max_tentativas - 1:
                time.sleep(delay_inicial * (2 ** tentativa))
                continue
            else:
                print("  Timeout após múltiplas tentativas.")
                return None
                
        except requests.exceptions.ConnectionError:
            print(f"  Erro de conexão na tentativa {tentativa + 1}")
            if tentativa < max_tentativas - 1:
                time.sleep(delay_inicial * (2 ** tentativa))
                continue
            else:
                print("  Erro de conexão após múltiplas tentativas.")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"  Erro na requisição: {e}")
            if tentativa < max_tentativas - 1:
                time.sleep(delay_inicial * (2 ** tentativa))
                continue
            else:
                return None
    
    return None

def verificar_rate_limit():
    """
    Verifica o status atual do rate limit usando a API REST.
    """
    try:
        response = requests.get(
            'https://api.github.com/rate_limit',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('resources', {}).get('search', {})
        else:
            print(f"Erro ao verificar rate limit: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Erro ao verificar rate limit: {e}")
        return None

def buscar_detalhes_repositorio(owner, repo_name):
    """
    Busca detalhes específicos de um repositório.
    """
    url = f"{REPO_BASE_URL}/{owner}/{repo_name}"
    
    # Informações básicas do repositório
    repo_data = fazer_requisicao_com_retry(url)
    if not repo_data:
        return None
    
    # Pausa pequena entre requisições
    time.sleep(0.1)
    
    # Busca pulls mergeados
    pulls_url = f"{url}/pulls"
    pulls_params = {'state': 'closed', 'per_page': 1, 'page': 1}
    pulls_response = fazer_requisicao_com_retry(pulls_url, pulls_params)
    
    # Extrai o número total de pulls do header Link (se disponível)
    merged_pulls_count = 0
    if pulls_response is not None:
        # Como é difícil contar pulls mergeados via API REST, usamos uma estimativa
        # baseada no número total de pulls fechados
        merged_pulls_count = repo_data.get('open_issues_count', 0) // 2  # Estimativa aproximada
    
    time.sleep(0.1)
    
    # Busca releases
    releases_url = f"{url}/releases"
    releases_params = {'per_page': 100}  # GitHub limita a 100 por página
    releases_response = fazer_requisicao_com_retry(releases_url, releases_params)
    releases_count = len(releases_response) if releases_response else 0
    
    time.sleep(0.1)
    
    # Busca issues fechadas (aproximação)
    issues_url = f"{url}/issues"
    closed_issues_params = {'state': 'closed', 'per_page': 1}
    closed_issues_response = fazer_requisicao_com_retry(issues_url, closed_issues_params)
    
    return {
        'repo_data': repo_data,
        'merged_pulls_count': merged_pulls_count,
        'releases_count': releases_count,
        'closed_issues_available': closed_issues_response is not None
    }

def main():
    """Função principal para buscar e processar os dados dos repositórios via API REST."""
    if not GITHUB_TOKEN or GITHUB_TOKEN == 'SEU_TOKEN_AQUI':
        print("ERRO: com token do GitHub no arquivo .env.")
        return

    # Verifica o rate limit inicial
    print("Verificando rate limit...")
    rate_limit_info = verificar_rate_limit()
    if rate_limit_info:
        print(f"Rate limit de busca: {rate_limit_info.get('remaining', 'N/A')}/{rate_limit_info.get('limit', 'N/A')}")
        reset_time = rate_limit_info.get('reset')
        if reset_time:
            reset_datetime = datetime.fromtimestamp(reset_time)
            print(f"Reset em: {reset_datetime}")
    
    all_repos = []
    repos_por_pagina = 30  # GitHub permite até 100, mas 30 é mais seguro
    total_repos_desejados = 100
    total_de_paginas = (total_repos_desejados + repos_por_pagina - 1) // repos_por_pagina
    
    print(f"\nBuscando os {total_repos_desejados} repositórios com mais estrelas...")
    print(f"Usando {repos_por_pagina} repositórios por página em {total_de_paginas} páginas")

    for page_num in range(1, total_de_paginas + 1):
        print(f"\n--- Página {page_num}/{total_de_paginas} ---")

        params = {
            'q': 'stars:>=1',
            'sort': 'stars',
            'order': 'desc',
            'per_page': repos_por_pagina,
            'page': page_num
        }

        # Faz a requisição de busca
        data = fazer_requisicao_com_retry(SEARCH_URL, params)
        
        if data is None:
            print(f"Falha ao obter dados da página {page_num}. Continuando...")
            continue

        repos_on_page = data.get('items', [])
        total_count = data.get('total_count', 0)

        if repos_on_page:
            all_repos.extend(repos_on_page)
            print(f"  Coletados {len(repos_on_page)} repositórios desta página.")
            print(f"  Total disponível no GitHub: {total_count:,}")
        else:
            print("  Nenhum repositório encontrado nesta página.")
            break

        # Pausa entre páginas para evitar rate limiting
        if page_num < total_de_paginas:
            delay = random.uniform(2, 4)  # Pausa mais longa para API REST
            print(f"  Aguardando {delay:.1f} segundos...")
            time.sleep(delay)
        
        # Para se já temos repositórios suficientes
        if len(all_repos) >= total_repos_desejados:
            all_repos = all_repos[:total_repos_desejados]
            break

    if not all_repos:
        print("\nNenhum repositório foi coletado com sucesso.")
        return
    
    # Processa os dados coletados
    repo_data_list = []
    print(f"\n--- Processando {len(all_repos)} repositórios ---")

    for i, repo in enumerate(all_repos):
        if not repo: 
            continue

        try:
            repo_name = repo['full_name']
            print(f"({i+1:3d}/{len(all_repos)}) {repo_name}")

            # Calcula dias desde última atualização
            pushed_at_str = repo.get('pushed_at', repo.get('updated_at', ''))
            if pushed_at_str:
                pushed_at = datetime.fromisoformat(pushed_at_str.replace('Z', '+00:00'))
                time_since_update_days = (datetime.now(timezone.utc) - pushed_at).days
            else:
                time_since_update_days = -1

            # Para simplificar e evitar muitas requisições adicionais,
            # usamos os dados básicos disponíveis na busca
            open_issues_count = repo.get('open_issues_count', 0)
            
            # Dados básicos do repositório
            repo_data = {
                'Repositorio': repo_name,
                'Estrelas': repo.get('stargazers_count', 0),
                'Linguagem_Primaria': repo.get('language', 'N/A') or 'N/A',
                'Data_de_Criacao': repo.get('created_at', '').split('T')[0] if repo.get('created_at') else 'N/A',
                'Dias_desde_Ultima_Atualizacao': time_since_update_days,
                'Pull_Requests_Aceitas': 'N/A',  # Requer requisições adicionais
                'Total_de_Releases': 'N/A',      # Requer requisições adicionais
                'Issues_Abertas': open_issues_count,
                'Forks': repo.get('forks_count', 0),
                'Tamanho_KB': repo.get('size', 0),
                'Razao_Issues_Fechadas_Total': 'N/A'  # Requer cálculo complexo
            }
            
            repo_data_list.append(repo_data)
            
        except Exception as e:
            print(f"    Erro ao processar repositório: {e}")
            continue

        # Pequena pausa para não sobrecarregar a API
        if i % 10 == 9:  # A cada 10 repositórios
            time.sleep(1)

    if not repo_data_list:
        print("Nenhum dado foi processado com sucesso.")
        return

    print(f"\nProcessamento concluído! {len(repo_data_list)} repositórios processados.")
    
    # Cria DataFrame e salva
    df = pd.DataFrame(repo_data_list)
    
    # Ordena por número de estrelas
    df = df.sort_values('Estrelas', ascending=False).reset_index(drop=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f'github_repos_rest_{timestamp}.csv'
    
    try:
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"\n✅ Dados exportados com sucesso para: '{csv_filename}'")
        print(f"   Total de repositórios: {len(df)}")
        print(f"   Arquivo salvo em: {os.path.abspath(csv_filename)}")
    except Exception as e:
        print(f"\n❌ Erro ao salvar arquivo CSV: {e}")
        return

    # Exibe estatísticas
    print("\n--- Estatísticas dos Dados ---")
    if len(df) > 0:
        print(f"Repositório com mais estrelas: {df.iloc[0]['Repositorio']} ({df.iloc[0]['Estrelas']:,} estrelas)")
        print(f"Linguagens mais populares:")
        lang_counts = df['Linguagem_Primaria'].value_counts().head(5)
        for lang, count in lang_counts.items():
            if lang != 'N/A':
                print(f"  {lang}: {count} repositórios")

    print("\n--- Amostra dos Dados (Top 10) ---")
    display_columns = ['Repositorio', 'Estrelas', 'Linguagem_Primaria', 'Forks']
    print(df[display_columns].head(10).to_string(index=False))


if __name__ == '__main__':
    main()