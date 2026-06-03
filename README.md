# Ponderada de Metricas CI/CD

Este repositorio contem um experimento pratico para medir um pipeline CI/CD no GitHub Actions. O projeto usa uma pequena biblioteca Python, testes automatizados e scripts proprios para coletar metricas reais de execucoes do workflow.

## Entregaveis

Os entregaveis principais estao organizados no indice [`entregaveis/README.md`](entregaveis/README.md). Links diretos:

- Relatorio tecnico final: [`REPORT.md`](REPORT.md)
- Workflow GitHub Actions: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)
- Script de coleta de metricas: [`scripts/collect_metrics.py`](scripts/collect_metrics.py)
- Script de geracao de graficos: [`scripts/generate_charts.py`](scripts/generate_charts.py)
- Base principal em CSV: [`data/pipeline_metrics.csv`](data/pipeline_metrics.csv)
- Base de etapas em CSV: [`data/step_metrics.csv`](data/step_metrics.csv)
- Manifesto de execucoes reais: [`data/run_manifest.csv`](data/run_manifest.csv)
- Base bruta/normalizada em JSON: [`data/raw_runs.json`](data/raw_runs.json)
- Graficos produzidos: [`charts/`](charts/)
- Matriz de variacoes executadas: [`experiments/run_matrix.csv`](experiments/run_matrix.csv)

## Resultado do experimento

Foram coletadas 12 execucoes reais do GitHub Actions, incluindo execucoes com cache habilitado/desabilitado, jobs sequenciais/paralelos, suites `fast`, `expanded`, `slow` e uma falha controlada. Os IDs reais dos workflows, commits e links para as execucoes estao documentados em [`REPORT.md`](REPORT.md).

## Estrutura

- `.github/workflows/ci.yml`: workflow parametrizado do experimento.
- `src/ci_metrics/`: pacote Python usado como alvo dos testes.
- `tests/`: suites `fast`, `expanded`, `slow` e falha controlada.
- `scripts/collect_metrics.py`: coleta metricas pela API do GitHub e artefatos JUnit.
- `scripts/generate_charts.py`: gera os graficos obrigatorios.
- `experiments/run_matrix.csv`: matriz de variacoes do experimento.
- `data/`: bases coletadas em CSV e JSON.
- `charts/`: graficos gerados a partir dos dados coletados.
- `entregaveis/`: indice dos arquivos que compoem a entrega.
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

A matriz do experimento esta em `experiments/run_matrix.csv`. Este repositorio ja contem 12 runs reais coletados em `data/run_manifest.csv`.

Comandos prontos para disparar a matriz estao em `experiments/run_commands.md`.

## Coleta de metricas

Crie um token com permissao de leitura para Actions e exporte:

```bash
export GITHUB_TOKEN=seu_token
make collect
```

Arquivos gerados:

- `data/pipeline_metrics.csv`
- `data/step_metrics.csv`
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

O arquivo [`REPORT.md`](REPORT.md) e o entregavel principal. Ele contem os links/IDs dos runs reais, commits usados, variacoes executadas, resultados inesperados e conclusoes com base nos dados coletados.
