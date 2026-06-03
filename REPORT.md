# Relatorio Tecnico: Analise de Metricas de Pipeline CI/CD

## 1. Contexto

Este experimento mede o comportamento de um pipeline CI/CD implementado no GitHub Actions. O repositorio contem um projeto Python pequeno, mas com gates reais de qualidade: instalacao de dependencias, lint, type checking, testes automatizados, geracao de artefatos e coleta automatizada de metricas.

O objetivo foi comparar execucoes reais com variacoes controladas de cache, paralelismo, volume de testes, testes lentos e falha controlada.

## 2. Links principais

- Repositorio GitHub: <https://github.com/Marlos001/ponderada-metricas-cicd>
- Workflow YAML: <https://github.com/Marlos001/ponderada-metricas-cicd/blob/main/.github/workflows/ci.yml>
- Script de coleta: [`scripts/collect_metrics.py`](scripts/collect_metrics.py)
- Base CSV principal: [`data/pipeline_metrics.csv`](data/pipeline_metrics.csv)
- Base de etapas: [`data/step_metrics.csv`](data/step_metrics.csv)
- Manifesto de runs: [`data/run_manifest.csv`](data/run_manifest.csv)
- Base JSON: [`data/raw_runs.json`](data/raw_runs.json)
- Matriz de execucoes: [`experiments/run_matrix.csv`](experiments/run_matrix.csv)

## 3. Hipoteses iniciais

1. O cache de dependencias deve reduzir pouco o tempo total, pois o projeto e pequeno e o custo dominante esperado esta nos testes.
2. O paralelismo entre jobs deve reduzir o tempo total em perfis mais longos, mas pode ter ganho baixo no perfil rapido devido ao overhead de inicializacao.
3. A quantidade de testes deve ter correlacao positiva com a duracao, mas testes lentos artificiais devem impactar mais do que muitos testes rapidos parametrizados.
4. Falhas que ocorrem cedo devem reduzir o tempo ate feedback, especialmente em lint/typecheck.

## 4. Desenho do experimento

O workflow `.github/workflows/ci.yml` possui quatro parametros:

- `cache_mode`: `enabled` ou `disabled`
- `execution_mode`: `sequential` ou `parallel`
- `test_profile`: `fast`, `expanded`, `slow` ou `failing`
- `pytest_workers`: `1` ou `auto`

Foram coletadas 12 execucoes reais no GitHub Actions. As variacoes cobrem:

- execucoes automaticas por `push`;
- execucoes manuais por `workflow_dispatch`;
- cache habilitado e desabilitado;
- jobs sequenciais e paralelos;
- perfil rapido com 16 testes;
- perfil expandido com 216 testes;
- perfil lento com 219 testes;
- falha controlada de teste.

## 5. Evidencias reais de execucao

| Run ID | Link | Commit | Mensagem | Variacao | Status |
| --- | --- | --- | --- | --- | --- |
| `26889292713` | <https://github.com/Marlos001/ponderada-metricas-cicd/actions/runs/26889292713> | `d249062` | `fix: validate metrics scripts and slow profile` | `push / cache enabled / parallel / fast` | success |
| `26889357301` | <https://github.com/Marlos001/ponderada-metricas-cicd/actions/runs/26889357301> | `e54358f` | `docs: add experiment run commands` | `push / cache enabled / parallel / fast` | success |
| `26890012236` | <https://github.com/Marlos001/ponderada-metricas-cicd/actions/runs/26890012236> | `6845ed0` | `fix: use project venv for metrics collection` | `push / cache enabled / parallel / fast` | success |
| `26890072807` | <https://github.com/Marlos001/ponderada-metricas-cicd/actions/runs/26890072807> | `ddec5fc` | `fix: handle in-progress workflow jobs` | `push / cache enabled / parallel / fast` | success |
| `26890387826` | <https://github.com/Marlos001/ponderada-metricas-cicd/actions/runs/26890387826> | `ddec5fc` | `fix: handle in-progress workflow jobs` | `dispatch / cache disabled / sequential / fast` | success |
| `26890412099` | <https://github.com/Marlos001/ponderada-metricas-cicd/actions/runs/26890412099> | `ddec5fc` | `fix: handle in-progress workflow jobs` | `dispatch / cache disabled / sequential / expanded` | success |
| `26890434399` | <https://github.com/Marlos001/ponderada-metricas-cicd/actions/runs/26890434399> | `ddec5fc` | `fix: handle in-progress workflow jobs` | `dispatch / cache enabled / sequential / expanded` | success |
| `26890471731` | <https://github.com/Marlos001/ponderada-metricas-cicd/actions/runs/26890471731> | `ddec5fc` | `fix: handle in-progress workflow jobs` | `dispatch / cache enabled / parallel / expanded / workers=1` | success |
| `26890492458` | <https://github.com/Marlos001/ponderada-metricas-cicd/actions/runs/26890492458> | `ddec5fc` | `fix: handle in-progress workflow jobs` | `dispatch / cache enabled / parallel / expanded / workers=auto` | success |
| `26890519546` | <https://github.com/Marlos001/ponderada-metricas-cicd/actions/runs/26890519546> | `ddec5fc` | `fix: handle in-progress workflow jobs` | `dispatch / cache enabled / sequential / slow` | success |
| `26890543332` | <https://github.com/Marlos001/ponderada-metricas-cicd/actions/runs/26890543332> | `ddec5fc` | `fix: handle in-progress workflow jobs` | `dispatch / cache enabled / parallel / slow / workers=auto` | success |
| `26890557964` | <https://github.com/Marlos001/ponderada-metricas-cicd/actions/runs/26890557964> | `ddec5fc` | `fix: handle in-progress workflow jobs` | `dispatch / cache enabled / parallel / failing` | failure |

## 6. Metricas coletadas

O script `scripts/collect_metrics.py` consulta a API do GitHub Actions e baixa os artefatos de teste quando disponiveis. A base final contem:

- ID do workflow run;
- SHA do commit;
- mensagem resumida do commit;
- status da execucao;
- duracao total do workflow;
- nome e duracao de cada job;
- nome e duracao de etapas relevantes;
- quantidade de testes;
- quantidade de falhas;
- tempo total e medio dos testes;
- timestamp da execucao;
- variacao experimental inferida.

Resumo dos runs:

| Perfil | Quantidade de runs | Duracao media do workflow |
| --- | ---: | ---: |
| `enabled / parallel / fast` | 4 | 37,5s |
| `disabled / sequential / fast` | 1 | 41,0s |
| `disabled / sequential / expanded` | 1 | 41,0s |
| `enabled / sequential / expanded` | 1 | 38,0s |
| `enabled / parallel / expanded` | 2 | 41,0s |
| `enabled / sequential / slow` | 1 | 43,0s |
| `enabled / parallel / slow` | 1 | 44,0s |
| `enabled / parallel / failing` | 1 | 43,0s |

## 7. Graficos

### 7.1 Tempo total do pipeline por execucao

![Tempo total por execucao](charts/workflow_duration_by_run.png)

### 7.2 Tempo por job

![Tempo por job](charts/job_duration_by_name.png)

### 7.3 Taxa de sucesso e falha

![Taxa de sucesso e falha](charts/success_failure_rate.png)

### 7.4 Quantidade de testes vs duracao

![Quantidade de testes vs duracao](charts/tests_vs_duration.png)

## 8. Analise dos resultados

### 8.1 Qual etapa mais contribuiu para o tempo total?

A etapa que mais contribuiu para o tempo total foi `Install dependencies`. A media por job ficou aproximadamente entre 17,6s e 18,8s:

- `typecheck / Install dependencies`: 18,75s
- `sequential-quality-gates / Install dependencies`: 18,25s
- `lint / Install dependencies`: 17,88s
- `tests / Install dependencies`: 17,62s

Isso foi maior que o tempo dos testes em si. Por exemplo, o perfil `expanded` executou 216 testes em cerca de 0,22s a 0,27s de tempo de pytest. O perfil `slow` executou 219 testes em cerca de 2,5s de tempo de pytest. Portanto, neste experimento, o gargalo dominante nao foi a logica testada, mas o custo recorrente de preparar ambiente em runners do GitHub Actions.

### 8.2 Houve diferenca significativa entre execucoes com e sem cache?

A diferenca existiu, mas foi pequena. A comparacao mais direta e o perfil `sequential / expanded`:

- sem cache: run `26890412099`, 41s;
- com cache: run `26890434399`, 38s.

O ganho observado foi de 3s, aproximadamente 7,3% do tempo total desse caso. Isso confirma parcialmente a hipotese inicial: cache ajudou, mas nao transformou o pipeline porque ainda existe custo fixo de runner, setup Python e instalacao/verificacao de dependencias.

### 8.3 O paralelismo reduziu o tempo total?

O paralelismo nao reduziu o tempo total nas comparacoes principais. No perfil `expanded` com cache:

- sequencial: 38s;
- paralelo: 41s e 41s.

No perfil `slow` com cache:

- sequencial: 43s;
- paralelo com `pytest-xdist`: 44s.

O resultado sugere que o projeto e pequeno demais para compensar o overhead de inicializar multiplos jobs. Em cada job paralelo, o workflow repete checkout, setup Python e instalacao de dependencias. Como esse custo domina o pipeline, dividir lint/typecheck/test em jobs paralelos nao gerou ganho liquido.

### 8.4 Quais falhas foram mais frequentes?

Houve 1 falha em 12 execucoes, totalizando taxa de falha de 8,3%. A falha foi controlada no perfil `failing`, com `test_profile=failing`, e ocorreu em teste automatizado. Nao foram observadas falhas acidentais de lint, typecheck, infraestrutura ou coleta de artefatos nos dados finais.

### 8.5 O pipeline fornece feedback rapido o suficiente?

Sim, para este projeto. As execucoes bem-sucedidas ficaram entre 36s e 44s. A falha controlada terminou em 43s. Para um projeto didatico, esse tempo e adequado para feedback rapido ao desenvolvedor.

No entanto, a analise tambem mostra que o feedback rapido depende do tamanho real do sistema. Aqui o tempo de teste e baixo, mas em um projeto maior o custo de instalacao repetido em jobs paralelos pode se tornar um gargalo ainda mais relevante.

### 8.6 Melhorias possiveis

Melhorias recomendadas:

- monitorar explicitamente cache hit/miss no CSV final;
- reduzir repeticao de instalacao em jobs paralelos, por exemplo usando artefatos de ambiente quando aplicavel;
- manter testes lentos isolados por marcador;
- separar suites lentas de suites rapidas em workflows diferentes quando o projeto crescer;
- aumentar a amostra por variacao para reduzir ruido de GitHub-hosted runners;
- adicionar falha controlada de lint em uma nova rodada, caso seja necessario comparar falha de qualidade estatica com falha de teste.

## 9. Resultados inesperados

1. O aumento de 16 para 216 testes quase nao aumentou o tempo total do workflow. O tempo total ficou em 41s tanto no run `disabled / sequential / fast` quanto no run `disabled / sequential / expanded`. Isso mostra que, neste projeto, muitos testes unitarios rapidos sao baratos perto do custo fixo de preparar o ambiente.
2. O paralelismo nao acelerou o perfil expandido. O run sequencial com cache terminou em 38s, enquanto os runs paralelos com cache terminaram em 41s. A expectativa inicial era que jobs paralelos ajudassem mais em suites maiores, mas o overhead de cada job foi maior que o ganho.
3. O perfil `slow` tambem nao se beneficiou do paralelismo com `pytest-xdist`: sequencial ficou em 43s e paralelo com workers automaticos ficou em 44s. O tempo adicional de coordenar workers e jobs superou a economia dos testes lentos, que ainda eram curtos em termos absolutos.

## 10. Comparacao entre hipotese e resultado observado

| Hipotese | Resultado observado | Confirmada? |
| --- | --- | --- |
| Cache reduz pouco o tempo total | Cache reduziu `sequential / expanded` de 41s para 38s | Sim |
| Paralelismo ajuda mais em suites longas | `parallel / expanded` ficou em 41s, contra 38s sequencial | Nao |
| Testes lentos pesam mais que muitos testes rapidos | `slow` ficou em 43-44s, acima de `expanded` em 38-41s | Sim, parcialmente |
| Falhas cedo reduzem tempo de feedback | Falha controlada terminou em 43s, semelhante aos runs lentos | Nao neste desenho |

## 11. Limitacoes

Limitacoes do experimento:

- A amostra possui 12 execucoes, suficiente para a atividade, mas pequena para inferencia estatistica robusta.
- Algumas variacoes possuem apenas uma repeticao, entao podem sofrer ruido do GitHub-hosted runner.
- O projeto e pequeno, entao o impacto de cache e paralelismo e menor do que em pipelines de sistemas grandes.
- Os testes lentos foram introduzidos de forma controlada, portanto simulam gargalo, mas nao representam necessariamente IO, banco, rede ou build real.
- A coleta identifica inputs pelo nome/metadados do workflow; mudancas futuras no formato do `run-name` podem exigir ajuste no script.
- O experimento coletou uma falha controlada de teste, mas nao uma falha controlada de lint.

## 12. Como a analise apoia decisoes de engenharia

A analise mostra que otimizar o pipeline sem medir pode levar a decisoes erradas. Antes dos dados, seria razoavel esperar que paralelismo reduzisse o tempo total. Depois da coleta, ficou claro que o gargalo estava em instalacao/setup repetido, nao no tempo de teste.

Em um time real, esse tipo de medicao ajuda a decidir onde investir: cache, reducao de setup, reorganizacao de jobs, separacao de suites ou paralelismo. Tambem evita adicionar complexidade ao CI quando o ganho observado e baixo.

## 13. Como reproduzir

1. Clonar o repositorio.
2. Instalar dependencias com `make install`.
3. Executar localmente `make lint`, `make typecheck` e os perfis de teste.
4. Rodar as variacoes em `experiments/run_matrix.csv` via GitHub Actions.
5. Exportar `GITHUB_TOKEN`.
6. Executar `make collect`.
7. Executar `make charts`.
8. Conferir os arquivos em `data/` e `charts/`.
