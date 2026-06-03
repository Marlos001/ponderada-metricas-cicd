# Ponderada de Metricas CI/CD

Este repositorio contem um experimento pratico para medir um pipeline CI/CD no GitHub Actions. O projeto usa uma pequena biblioteca Python, testes automatizados e scripts proprios para coletar metricas reais de execucoes do workflow.

## Estrutura

- `.github/workflows/ci.yml`: workflow parametrizado do experimento.
- `src/ci_metrics/`: pacote Python usado como alvo dos testes.
- `tests/`: suites `fast`, `expanded`, `slow` e falha controlada.
- `scripts/collect_metrics.py`: coleta metricas pela API do GitHub e artefatos JUnit.
- `scripts/generate_charts.py`: gera os graficos obrigatorios.
- `experiments/run_matrix.csv`: matriz recomendada de 14 execucoes reais.
- `REPORT.md`: relatorio tecnico em PT-BR.

## Reproducao local

```bash
python -m venv .venv
source .venv/bin/activate
make install
make lint
make typecheck
make test-fast
make test-expanded
make test-slow
```

Para executar a falha controlada localmente:

```bash
make test-failing
```

## Execucao do experimento no GitHub Actions

O workflow aceita quatro parametros:

- `cache_mode`: `enabled` ou `disabled`
- `execution_mode`: `sequential` ou `parallel`
- `test_profile`: `fast`, `expanded`, `slow` ou `failing`
- `pytest_workers`: `1` ou `auto`

A matriz recomendada esta em `experiments/run_matrix.csv`. Execute pelo menos 12 runs reais; este projeto recomenda 14 para incluir falhas controladas.

## Coleta de metricas

Crie um token com permissao de leitura para Actions e exporte:

```bash
export GITHUB_TOKEN=seu_token
make collect
```

Arquivos gerados:

- `data/pipeline_metrics.csv`
- `data/run_manifest.csv`
- `data/raw_runs.json`

## Geracao de graficos

```bash
make charts
```

Graficos gerados:

- `charts/workflow_duration_by_run.png`
- `charts/job_duration_by_name.png`
- `charts/success_failure_rate.png`
- `charts/tests_vs_duration.png`

## Relatorio

O arquivo `REPORT.md` e o entregavel principal. Depois das execucoes reais, preencha os links/IDs dos runs, commits usados, resultados inesperados e conclusoes com base nos dados coletados.
