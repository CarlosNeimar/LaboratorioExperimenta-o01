import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def metricas_repositorios_populares(arq_csv):

    df = pd.read_csv(arq_csv)

    if df.empty:
        print("\nDataframe vazio, não há dados para calcular métricas.")
        return
    
    # RQ1: Idade mediana dos repositórios
    idade_media_repos = df['repository_age_days'].median()
    print(f"Idade mediana dos repositórios (em dias): {idade_media_repos:.2f}")

    # RQ2: Total de pull requests aceitos
    total_pr_aceitos = df['accepted_pull_requests'].sum()
    print(f"Total de pull requests aceitos: {total_pr_aceitos}")

    # RQ3: Frequência lancamento releases
    df['releases_per_year'] = df['total_releases'] / (df['repository_age_days'] / 365.25)
    freq_lancamento_releases = df['releases_per_year'].median()
    print(f"Frequência mediana de lançamento de releases por ano: {freq_lancamento_releases:.2f}")

    # RQ4: Tempo médio desde a última atualização
    tempo_medio_ultima_atualizacao = df['days_since_last_update'].median()
    print(f"Tempo médio desde a última atualização (em dias): {tempo_medio_ultima_atualizacao:.2f}")

    # RQ5: Linguagens de programação mais comuns
    linguagens_comuns = df['primary_language'].value_counts().head(10)
    print("Linguagens de programação mais comuns entre os repositórios:")
    print(linguagens_comuns)

    # RQ6: Razao de issues fechadas para issues totais
    df['issue_closure_rate'] = df['closed_issues'] / df['total_issues']
    razao_issues_fechadas = df['issue_closure_rate'].median()
    print(f"Razão mediana de issues fechadas para issues totais: {razao_issues_fechadas:.2f}")    



# Visualizações

def visualizacoes_metricas(arq_csv):
    df = pd.read_csv(arq_csv)

    if df.empty:
        print("\nDataframe vazio, não há dados para analisar.")
        return

    sns.set_theme(style="whitegrid")
    
    print("Gerando visualizações e análises...")

    # --- RQ01: Sistemas populares são maduros/antigos? ---
    plt.figure(figsize=(10, 6))
    sns.histplot(df['repository_age_days'], kde=True, bins=30)
    idade_mediana = df['repository_age_days'].median()
    plt.axvline(idade_mediana, color='red', linestyle='--', linewidth=2, label=f'Mediana: {idade_mediana:.0f} dias')
    plt.title('RQ01: Distribuição da Idade dos Repositórios Populares', fontsize=16)
    plt.xlabel('Idade em Dias')
    plt.ylabel('Contagem de Repositórios')
    plt.legend()
    plt.savefig('RQ01_idade_repositorios.png')
    plt.close()

    # --- RQ02: Sistemas populares recebem muita contribuição externa? ---
    top_10_languages = df['primary_language'].value_counts().head(10).index
    df_top_lang = df[df['primary_language'].isin(top_10_languages)]
    median_prs_by_lang = df_top_lang.groupby('primary_language')['accepted_pull_requests'].median().sort_values(ascending=False)
    plt.figure(figsize=(12, 8))
    sns.barplot(x=median_prs_by_lang.values, y=median_prs_by_lang.index, palette='magma', orient='h')
    plt.title('RQ02: Mediana de Pull Requests Aceitas por Linguagem', fontsize=16)
    plt.xlabel('Mediana de Pull Requests Aceitas')
    plt.ylabel('Linguagem Primária')
    plt.tight_layout()
    plt.savefig('RQ02_comparacao_linguagens.png', dpi=150)
    plt.close()

    # --- RQ03: Sistemas populares lançam releases com frequência? ---
    df['releases_per_year'] = df['total_releases'] / (df['repository_age_days'] / 365.25)
    # Removendo outliers para melhor visualização
    df_releases_filtered = df[df['releases_per_year'] < df['releases_per_year'].quantile(0.95)]
    plt.figure(figsize=(10, 6))
    sns.histplot(df_releases_filtered['releases_per_year'], kde=True, bins=25)
    releases_mediana = df['releases_per_year'].median()
    plt.axvline(releases_mediana, color='red', linestyle='--', linewidth=2, label=f'Mediana: {releases_mediana:.2f} releases/ano')
    plt.title('RQ03: Frequência Anual de Releases (95% dos dados)', fontsize=16)
    plt.xlabel('Releases por Ano')
    plt.ylabel('Contagem de Repositórios')
    plt.legend()
    plt.savefig('RQ03_frequencia_releases.png')
    plt.close()

    # --- RQ04: Sistemas populares são atualizados com frequência? ---
    plt.figure(figsize=(10, 6))
    sns.histplot(df['days_since_last_update'], kde=True, bins=30)
    atualizacao_mediana = df['days_since_last_update'].median()
    plt.axvline(atualizacao_mediana, color='red', linestyle='--', linewidth=2, label=f'Mediana: {atualizacao_mediana:.0f} dias')
    plt.title('RQ04: Tempo Desde a Última Atualização', fontsize=16)
    plt.xlabel('Dias Desde a Última Atualização')
    plt.ylabel('Contagem de Repositórios')
    plt.legend()
    plt.savefig('RQ04_ultima_atualizacao.png')
    plt.close()

    # --- RQ05: Sistemas populares são escritos nas linguagens mais populares? ---
    plt.figure(figsize=(12, 8))
    linguagens_comuns = df['primary_language'].value_counts().head(10)
    sns.barplot(x=linguagens_comuns.values, y=linguagens_comuns.index, palette='viridis', orient='h')
    plt.title('RQ05: 10 Linguagens de Programação Mais Comuns', fontsize=16)
    plt.xlabel('Número de Repositórios')
    plt.ylabel('Linguagem')
    plt.tight_layout()
    plt.savefig('RQ05_linguagens_populares.png')
    plt.close()

    # --- RQ06: Sistemas populares possuem um alto percentual de issues fechadas? ---
    df['issue_closure_rate'] = df.apply(
        lambda row: row['closed_issues'] / row['total_issues'] if row['total_issues'] > 0 else 0,
        axis=1
    )
    plt.figure(figsize=(10, 6))
    sns.histplot(df['issue_closure_rate'], kde=True, bins=20)
    razao_mediana = df['issue_closure_rate'].median()
    plt.axvline(razao_mediana, color='red', linestyle='--', linewidth=2, label=f'Mediana: {razao_mediana:.2f}')
    plt.title('RQ06: Distribuição da Razão de Issues Fechadas', fontsize=16)
    plt.xlabel('Razão (Issues Fechadas / Issues Totais)')
    plt.ylabel('Contagem de Repositórios')
    plt.legend()
    plt.savefig('RQ06_razao_issues.png')
    plt.close()
    
    print("\nVisualizações salvas como arquivos .png!")

if __name__ == '__main__':

    # metricas_repositorios_populares('repositorios_populares.csv')
    visualizacoes_metricas('repositorios_populares.csv')