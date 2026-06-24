"""
LAB05 - Gerador do Dashboard em HTML puro (sem React, sem npm, sem servidor)

Lê os CSVs reais em data/ e gera output/dashboard.html — um único arquivo HTML
autocontido que você abre clicando duas vezes (funciona em qualquer navegador,
sem precisar instalar nada).

Uso:
  python gerar_dashboard_html.py
"""

import os
import json
import pandas as pd
import scipy.stats as stats

BASE = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(BASE, "data")

df = pd.read_csv(os.path.join(DATA_DIR, "resultados_limpos.csv"))
desc = pd.read_csv(os.path.join(DATA_DIR, "estatisticas_descritivas.csv"))
testes = pd.read_csv(os.path.join(DATA_DIR, "testes_hipotese.csv"))


def get_desc(tratamento, metrica_label):
    return desc[(desc["tratamento"] == tratamento) & (desc["metrica"] == metrica_label)].iloc[0]


desc_rest_tempo = get_desc("REST", "Tempo de Resposta (ms)")
desc_gql_tempo = get_desc("GraphQL", "Tempo de Resposta (ms)")
desc_rest_tam = get_desc("REST", "Tamanho da Resposta (bytes)")
desc_gql_tam = get_desc("GraphQL", "Tamanho da Resposta (bytes)")

teste_rq1 = testes[testes["RQ"] == "RQ1"].iloc[0]
teste_rq2 = testes[testes["RQ"] == "RQ2"].iloc[0]

n_repos = df["repositorio"].nunique()
n_rest = int(desc_rest_tempo["n"])
n_gql = int(desc_gql_tempo["n"])
n_total = n_rest + n_gql

agg = (
    df.groupby(["repositorio", "tratamento"])
    .agg(tempo_medio=("tempo_resposta_ms", "mean"), tamanho_medio=("tamanho_resposta_bytes", "mean"))
    .reset_index()
)
agg["tempo_medio"] = agg["tempo_medio"].round(2)
agg["tamanho_medio"] = agg["tamanho_medio"].round(2)

repos = sorted(df["repositorio"].unique())
tempo_rest = [float(agg[(agg.repositorio == r) & (agg.tratamento == "REST")]["tempo_medio"].iloc[0]) for r in repos]
tempo_gql = [float(agg[(agg.repositorio == r) & (agg.tratamento == "GraphQL")]["tempo_medio"].iloc[0]) for r in repos]
tam_rest = [float(agg[(agg.repositorio == r) & (agg.tratamento == "REST")]["tamanho_medio"].iloc[0]) for r in repos]
tam_gql = [float(agg[(agg.repositorio == r) & (agg.tratamento == "GraphQL")]["tamanho_medio"].iloc[0]) for r in repos]
repos_labels = [r.split("/")[1] if "/" in r else r for r in repos]


def fmt_br(valor, decimais=2):
    s = f"{valor:,.{decimais}f}"
    return s.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")


def fmt_p(p):
    return "&lt; 0,001" if p < 0.001 else fmt_br(p, 4)


rq1_sig = bool(teste_rq1["significativo_5pct"])
rq2_sig = bool(teste_rq2["significativo_5pct"])
mais_rapido = "GraphQL" if desc_gql_tempo["media"] < desc_rest_tempo["media"] else "REST"
menor_payload = "GraphQL" if desc_gql_tam["media"] < desc_rest_tam["media"] else "REST"

reducao_tempo_pct = (desc_rest_tempo["media"] - desc_gql_tempo["media"]) / desc_rest_tempo["media"] * 100
reducao_tam_pct = (desc_rest_tam["media"] - desc_gql_tam["media"]) / desc_rest_tam["media"] * 100

html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>LAB05 — GraphQL vs REST — Dashboard de Resultados</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #f4f5f7; margin: 0; padding: 24px; color: #1f2937;
  }}
  .wrap {{ max-width: 1100px; margin: 0 auto; }}
  h1 {{ font-size: 26px; font-weight: 800; margin: 0 0 4px; }}
  .subtitle {{ color: #6b7280; font-size: 14px; margin-bottom: 24px; }}
  .cards {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
  .card {{ background: #fff; border-radius: 12px; padding: 20px 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); flex: 1; min-width: 220px; }}
  .card-label {{ font-size: 13px; color: #8a8a8a; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; }}
  .card-values {{ display: flex; gap: 24px; margin-bottom: 10px; }}
  .card-values .rest-label {{ font-size: 12px; color: #4C72B0; font-weight: 600; }}
  .card-values .gql-label {{ font-size: 12px; color: #DD8452; font-weight: 600; }}
  .card-values .value {{ font-size: 22px; font-weight: 700; }}
  .badge {{ font-size: 13px; color: #059669; font-weight: 600; background: #ecfdf5; display: inline-block; padding: 4px 10px; border-radius: 6px; }}
  .tests-panel {{ background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 24px; }}
  .tests-panel-label {{ font-size: 13px; color: #8a8a8a; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px; }}
  .tests-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  @media (max-width: 700px) {{ .tests-grid {{ grid-template-columns: 1fr; }} }}
  .test-box {{ border: 1px solid #e5e7eb; border-radius: 8px; padding: 14px; }}
  .test-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }}
  .test-title {{ font-weight: 700; }}
  .test-sig {{ font-size: 12px; font-weight: 700; padding: 3px 8px; border-radius: 6px; }}
  .test-sig.yes {{ color: #059669; background: #ecfdf5; }}
  .test-sig.no {{ color: #dc2626; background: #fef2f2; }}
  .test-body {{ font-size: 13px; color: #6b7280; line-height: 1.6; }}
  .toggle {{ display: flex; gap: 8px; margin-bottom: 16px; }}
  .toggle button {{
    padding: 8px 16px; border-radius: 8px; border: none; cursor: pointer;
    font-weight: 600; font-size: 13px; background: #fff; color: #6b7280;
    box-shadow: 0 1px 2px rgba(0,0,0,0.06);
  }}
  .toggle button.active {{ background: #1f2937; color: #fff; }}
  .chart-panel {{ background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 24px; }}
  .chart-title {{ font-size: 14px; font-weight: 700; margin-bottom: 16px; }}
  .footer {{ font-size: 12px; color: #9ca3af; text-align: center; padding-bottom: 12px; }}
</style>
</head>
<body>
<div class="wrap">

  <h1>GraphQL vs REST — Dashboard de Resultados</h1>
  <div class="subtitle">Experimento controlado · API do GitHub · {n_repos} repositórios · {n_total} medições válidas analisadas</div>

  <div class="cards">
    <div class="card">
      <div class="card-label">Tempo de Resposta (média)</div>
      <div class="card-values">
        <div><div class="rest-label">REST</div><div class="value">{fmt_br(desc_rest_tempo['media'])} ms</div></div>
        <div><div class="gql-label">GraphQL</div><div class="value">{fmt_br(desc_gql_tempo['media'])} ms</div></div>
      </div>
      <div class="badge">{'↓' if reducao_tempo_pct > 0 else '↑'} {fmt_br(abs(reducao_tempo_pct), 1)}% com {mais_rapido}</div>
    </div>
    <div class="card">
      <div class="card-label">Tamanho da Resposta (média)</div>
      <div class="card-values">
        <div><div class="rest-label">REST</div><div class="value">{fmt_br(desc_rest_tam['media'], 0)} B</div></div>
        <div><div class="gql-label">GraphQL</div><div class="value">{fmt_br(desc_gql_tam['media'], 0)} B</div></div>
      </div>
      <div class="badge">{'↓' if reducao_tam_pct > 0 else '↑'} {fmt_br(abs(reducao_tam_pct), 1)}% com {menor_payload}</div>
    </div>
  </div>

  <div class="tests-panel">
    <div class="tests-panel-label">Testes de Hipótese (α = 0,05)</div>
    <div class="tests-grid">
      <div class="test-box">
        <div class="test-header">
          <span class="test-title">RQ1 — Tempo de Resposta</span>
          <span class="test-sig {'yes' if rq1_sig else 'no'}">{'SIGNIFICATIVO' if rq1_sig else 'NÃO SIGNIFICATIVO'}</span>
        </div>
        <div class="test-body">
          Teste: {teste_rq1['teste']}<br>
          Estatística: {fmt_br(abs(teste_rq1['estatistica']))} · p-valor: {fmt_p(teste_rq1['p_valor'])}<br>
          Diferença mediana (REST − GraphQL): <strong>{fmt_br(abs(teste_rq1['diferenca_mediana_REST_menos_GraphQL']))} ms</strong>
        </div>
      </div>
      <div class="test-box">
        <div class="test-header">
          <span class="test-title">RQ2 — Tamanho da Resposta</span>
          <span class="test-sig {'yes' if rq2_sig else 'no'}">{'SIGNIFICATIVO' if rq2_sig else 'NÃO SIGNIFICATIVO'}</span>
        </div>
        <div class="test-body">
          Teste: {teste_rq2['teste']}<br>
          Estatística: {fmt_br(abs(teste_rq2['estatistica']))} · p-valor: {fmt_p(teste_rq2['p_valor'])}<br>
          Diferença mediana (REST − GraphQL): <strong>{fmt_br(abs(teste_rq2['diferenca_mediana_REST_menos_GraphQL']), 0)} bytes</strong>
        </div>
      </div>
    </div>
  </div>

  <div class="toggle">
    <button id="btn-tempo" class="active" onclick="mostrar('tempo')">Tempo de Resposta</button>
    <button id="btn-tamanho" onclick="mostrar('tamanho')">Tamanho da Resposta</button>
  </div>

  <div class="chart-panel">
    <div class="chart-title" id="chart-title">Tempo Médio de Resposta por Repositório</div>
    <canvas id="grafico" height="110"></canvas>
  </div>

  <div class="footer">LAB05 · Laboratório de Experimentação de Software · PUC Minas</div>
</div>

<script>
const repos = {json.dumps(repos_labels, ensure_ascii=False)};
const tempoRest = {json.dumps(tempo_rest)};
const tempoGql = {json.dumps(tempo_gql)};
const tamRest = {json.dumps(tam_rest)};
const tamGql = {json.dumps(tam_gql)};

const ctx = document.getElementById('grafico').getContext('2d');
let chart = new Chart(ctx, {{
  type: 'bar',
  data: {{
    labels: repos,
    datasets: [
      {{ label: 'REST', data: tempoRest, backgroundColor: '#4C72B0', borderRadius: 4 }},
      {{ label: 'GraphQL', data: tempoGql, backgroundColor: '#DD8452', borderRadius: 4 }}
    ]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ position: 'top' }} }},
    scales: {{ y: {{ title: {{ display: true, text: 'ms' }} }} }}
  }}
}});

function mostrar(tipo) {{
  document.getElementById('btn-tempo').classList.toggle('active', tipo === 'tempo');
  document.getElementById('btn-tamanho').classList.toggle('active', tipo === 'tamanho');
  document.getElementById('chart-title').innerText = tipo === 'tempo'
    ? 'Tempo Médio de Resposta por Repositório'
    : 'Tamanho Médio de Resposta por Repositório';

  chart.data.datasets[0].data = tipo === 'tempo' ? tempoRest : tamRest;
  chart.data.datasets[1].data = tipo === 'tempo' ? tempoGql : tamGql;
  chart.options.scales.y.title.text = tipo === 'tempo' ? 'ms' : 'bytes';
  chart.update();
}}
</script>
</body>
</html>
"""

out_path = os.path.join(BASE, "dashboard.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Dashboard HTML gerado em {out_path}")
print("Basta abrir esse arquivo clicando duas vezes — funciona offline, exceto pelo Chart.js (CDN, requer internet apenas no carregamento).")
