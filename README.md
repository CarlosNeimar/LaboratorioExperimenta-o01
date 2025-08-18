-----

# Laboratório 01: Características de Repositórios Populares no GitHub

**Disciplina:** LABORATÓRIO DE EXPERIMENTAÇÃO DE SOFTWARE

**Curso:** ENGENHARIA DE SOFTWARE

-----

## 1\. Visão Geral do Projeto

Este projeto visa estudar as principais características de sistemas open-source populares, analisando os 1.000 repositórios com o maior número de estrelas no GitHub.

O script em Python foi desenvolvido para automatizar a coleta de dados. Ele utiliza a **API REST do GitHub** para:

1.  Buscar os repositórios com o maior número de estrelas.
2.  Para cada repositório, coletar métricas detalhadas, como idade, número de Pull Requests aceitos, total de releases e a razão de issues fechadas.

## 2\. Pré-requisitos

  * Python 3.8 ou superior.
  * Um **Token de Acesso Pessoal (PAT)** do GitHub. Ele é essencial para aumentar o limite de requisições à API e permitir a coleta dos dados.

## 3\. Instalação e Configuração

1.  **Clone o repositório:**

    ```bash
    git clone https://github.com/CarlosNeimar/LaboratorioExperimenta-o01
    cd LaboratorioExperimenta-o01
    ```

2.  **Configure seu Token de Acesso:**
    Crie um arquivo chamado `.env` na raiz do projeto e adicione seu token da seguinte forma:

    ```
    GITHUB_TOKEN="seu_token_aqui"
    ```

## 4\. Exemplo de Saída (Execução com 10 repositórios)

Abaixo, exemplo do console após execução:

```text
Buscando os 10 repositórios com mais estrelas...
Usando 25 repositórios por página em 1 páginas

--- Página 1/1 ---
    Tentativa 1/5...
    Rate limit restante: 29
    Coletados 25 repositórios desta página.
    Total disponível no GitHub: 26,159,473

--- Processando 10 repositórios ---
Este processo pode demorar devido às requisições adicionais para obter dados completos.
(  1/10) freeCodeCamp/freeCodeCamp
      Buscando detalhes adicionais...
    Tentativa 1/5...
    Rate limit restante: 4981
          PR: Mais de 100 PRs encontrados, contando páginas adicionais...
          Issues: Mais de 100 issues fechadas, fazendo estimativa...
          PRs mergeados: 200, Releases: 0, Razão issues fechadas: 0.75
(  2/10) codecrafters-io/build-your-own-x
      Buscando detalhes adicionais...
    Tentativa 1/5...
    Rate limit restante: 4973
          PRs mergeados: 142, Releases: 0, Razão issues fechadas: 0.75
...

Processamento concluído! 10 repositórios processados.

 Dados exportados com sucesso para: 'result\2025-08-18_02-32-47.csv'
    Total de repositórios: 10
    Arquivo salvo em: D:\LaboratorioExperimenta-o01\result\2025-08-18_02-32-47.csv

--- Estatísticas dos Dados ---
Repositório com mais estrelas: freeCodeCamp/freeCodeCamp (425,926 estrelas)
Média de PRs aceitas: 132.8
Média de releases: 0.1
Média de razão issues fechadas: 0.800
Linguagens mais populares:
   Python: 4 repositórios
   TypeScript: 2 repositórios
   Markdown: 1 repositórios

--- Amostra dos Dados (Top 10) ---
                                 Repositorio   Estrelas   Pull_Requests_Aceitas   Total_de_Releases   Razao_Issues_Fechadas_Total
                   freeCodeCamp/freeCodeCamp     425926                     200                   0                         0.750
          codecrafters-io/build-your-own-x     411437                     142                   0                         0.750
                        sindresorhus/awesome     392605                      69                   0                         0.852
  EbookFoundation/free-programming-books     365260                     188                   0                         0.882
```
