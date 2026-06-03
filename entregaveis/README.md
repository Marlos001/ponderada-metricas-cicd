# Indice de Entregaveis

Esta pasta funciona como um indice de correcao. Os arquivos oficiais ficam nas pastas do projeto para manter os caminhos executaveis e reproduziveis.

## Entrega principal

- Relatorio tecnico final: [`../REPORT.md`](../REPORT.md)
- Repositorio GitHub: <https://github.com/Marlos001/ponderada-metricas-cicd>

## Pipeline CI/CD

- Workflow YAML: [`../.github/workflows/ci.yml`](../.github/workflows/ci.yml)
- Matriz de variacoes: [`../experiments/run_matrix.csv`](../experiments/run_matrix.csv)
- Comandos de execucao: [`../experiments/run_commands.md`](../experiments/run_commands.md)

## Scripts obrigatorios

- Coleta de metricas: [`../scripts/collect_metrics.py`](../scripts/collect_metrics.py)
- Geracao de graficos: [`../scripts/generate_charts.py`](../scripts/generate_charts.py)

## Bases geradas

- Dataset principal: [`../data/pipeline_metrics.csv`](../data/pipeline_metrics.csv)
- Manifesto de runs reais: [`../data/run_manifest.csv`](../data/run_manifest.csv)
- Duracao por etapa: [`../data/step_metrics.csv`](../data/step_metrics.csv)
- Dados normalizados em JSON: [`../data/raw_runs.json`](../data/raw_runs.json)

## Graficos

- Tempo total do pipeline por execucao: [`../charts/workflow_duration_by_run.png`](../charts/workflow_duration_by_run.png)
- Tempo medio por job: [`../charts/job_duration_by_name.png`](../charts/job_duration_by_name.png)
- Taxa de sucesso e falha: [`../charts/success_failure_rate.png`](../charts/success_failure_rate.png)
- Quantidade de testes vs duracao: [`../charts/tests_vs_duration.png`](../charts/tests_vs_duration.png)

## Evidencias reais

Os 12 IDs reais de workflow, links para GitHub Actions, commits e variacoes estao na secao "Evidencias reais de execucao" do [`../REPORT.md`](../REPORT.md).
