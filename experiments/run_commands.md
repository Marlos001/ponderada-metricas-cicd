# Comandos para executar a matriz do experimento

Os comandos abaixo disparam as execucoes planejadas no GitHub Actions. Eles assumem que o `gh` esta autenticado no repositorio.

```bash
gh workflow run ci.yml -f cache_mode=disabled -f execution_mode=sequential -f test_profile=fast -f pytest_workers=1
gh workflow run ci.yml -f cache_mode=disabled -f execution_mode=sequential -f test_profile=fast -f pytest_workers=1
gh workflow run ci.yml -f cache_mode=enabled -f execution_mode=sequential -f test_profile=fast -f pytest_workers=1
gh workflow run ci.yml -f cache_mode=enabled -f execution_mode=sequential -f test_profile=fast -f pytest_workers=1
gh workflow run ci.yml -f cache_mode=enabled -f execution_mode=parallel -f test_profile=fast -f pytest_workers=1
gh workflow run ci.yml -f cache_mode=enabled -f execution_mode=parallel -f test_profile=fast -f pytest_workers=1
gh workflow run ci.yml -f cache_mode=disabled -f execution_mode=sequential -f test_profile=expanded -f pytest_workers=1
gh workflow run ci.yml -f cache_mode=enabled -f execution_mode=sequential -f test_profile=expanded -f pytest_workers=1
gh workflow run ci.yml -f cache_mode=enabled -f execution_mode=parallel -f test_profile=expanded -f pytest_workers=1
gh workflow run ci.yml -f cache_mode=enabled -f execution_mode=parallel -f test_profile=expanded -f pytest_workers=auto
gh workflow run ci.yml -f cache_mode=enabled -f execution_mode=sequential -f test_profile=slow -f pytest_workers=1
gh workflow run ci.yml -f cache_mode=enabled -f execution_mode=parallel -f test_profile=slow -f pytest_workers=auto
gh workflow run ci.yml -f cache_mode=enabled -f execution_mode=parallel -f test_profile=failing -f pytest_workers=1
```

Para a falha controlada de lint, faca um commit temporario com um erro simples de lint, como um import nao usado, rode o workflow e depois faca um commit de correcao. Use mensagens explicitas:

```bash
git commit -m "experiment: introduce controlled lint failure"
git commit -m "experiment: fix controlled lint failure"
```

Essa falha deve aparecer no relatorio como variacao planejada, nao como erro acidental.
