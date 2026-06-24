# LAB05 — GraphQL vs REST — Experimento Controlado

Este pacote já contém os resultados da SUA coleta real (rodada em 24/06/2026),
processados e prontos. Você não precisa rodar nada para ver os resultados —
mas se quiser refazer tudo do zero (ex: coletar de novo, mudar repositórios),
o passo a passo está abaixo.

## O que já está pronto, sem você fazer nada

- ✅ `data/` — seus CSVs reais (brutos, limpos, estatísticas, testes)
- ✅ `graficos/` — 6 gráficos gerados a partir dos seus dados reais
- ✅ `relatorio/Relatorio_Final_LAB05.docx` — relatório completo com os números reais
- ✅ `dashboard.html` — **dashboard interativo, abra clicando duas vezes, sem instalar nada**

## Como abrir o dashboard

Dê duplo clique em `dashboard.html`. Ele abre no seu navegador padrão (Chrome, Edge,
Firefox, etc.) e já mostra os gráficos e números reais. Não precisa de Node, npm,
React ou qualquer instalação — é um arquivo HTML autocontido (usa Chart.js via CDN,
então precisa de internet só para carregar a biblioteca de gráficos na primeira vez).

## Resultados principais (já calculados com seus dados reais)

| Métrica | REST (média) | GraphQL (média) | Diferença |
|---|---|---|---|
| Tempo de Resposta | ~1.383 ms | ~637 ms | GraphQL ~54% mais rápido |
| Tamanho da Resposta | ~29.371 bytes | ~765 bytes | GraphQL ~97% menor |

Ambos os testes de hipótese (Wilcoxon pareado, pois os dados não passaram no teste
de normalidade Shapiro-Wilk) deram **estatisticamente significativos** (p < 0,001),
rejeitando H0₁ e H0₂.

## Se quiser refazer o experimento do zero

1. Gere um Personal Access Token no GitHub: https://github.com/settings/tokens
2. ```bash
   pip install requests pandas matplotlib seaborn scipy
   export GITHUB_TOKEN="seu_token_aqui"
   cd scripts
   python coletar_dados.py
   ```
3. ```bash
   python analisar_dados.py
   python gerar_graficos.py
   ```
4. Para atualizar o relatório Word e o dashboard automaticamente com os novos números
   (sem editar nada na mão):
   ```bash
   python atualizar_relatorio_e_dashboard.py
   node gerar_relatorio.js          # requer: npm install -g docx (uma vez só)
   python gerar_dashboard_html.py
   ```

   **Resumo do fluxo completo:**
   ```bash
   export GITHUB_TOKEN="seu_token"
   python coletar_dados.py
   python analisar_dados.py
   python gerar_graficos.py
   python atualizar_relatorio_e_dashboard.py
   node gerar_relatorio.js
   python gerar_dashboard_html.py
   ```

## Estrutura do pacote

```
dashboard.html  → Sprint 3 (Passo 6): dashboard interativo, abre direto no navegador

scripts/
  coletar_dados.py                    → Sprint 1 (Passo 2) / Sprint 2 (Passo 3): coleta via API do GitHub
  simular_dados.py                    → gera dataset sintético (só para testar o pipeline sem token)
  analisar_dados.py                   → Sprint 2 (Passo 4): limpeza, descritivas, testes de hipótese
  gerar_graficos.py                   → Sprint 2/3 (Passo 6): boxplots, histogramas, barras (.png)
  atualizar_relatorio_e_dashboard.py  → lê os CSVs e regenera gerar_relatorio.js com os números reais
  gerar_relatorio.js                  → Sprint 2 (Passo 5): gera o relatório Word a partir dos dados atuais
  gerar_dashboard_html.py             → lê os CSVs e gera dashboard.html (sem precisar de React/npm)

data/
  resultados_brutos.csv         → medições brutas (uma linha por chamada de API)
  resultados_limpos.csv         → após remoção de falhas e outliers
  estatisticas_descritivas.csv  → média, mediana, dp, etc. por tratamento/métrica
  testes_hipotese.csv           → resultado dos testes estatísticos para RQ1 e RQ2

graficos/
  6 arquivos .png (boxplots, histogramas, barras por repositório)

relatorio/
  Relatorio_Final_LAB05.docx → relatório completo (introdução, metodologia, resultados, discussão)
```

## Desenho do experimento (resumo)

- **RQ1**: tempo de resposta GraphQL vs REST
- **RQ2**: tamanho de resposta GraphQL vs REST
- **Objeto experimental**: 10 repositórios públicos do GitHub (mesmo conjunto nos 2 tratamentos)
- **Tratamentos**: API REST (2 chamadas: repo + issues) vs API GraphQL (1 chamada equivalente)
- **Design**: pareado (within-subject) — cada repositório é medido nos dois tratamentos
- **Análise**: Shapiro-Wilk (normalidade) → t-Student pareado ou Wilcoxon pareado (α=0,05)
