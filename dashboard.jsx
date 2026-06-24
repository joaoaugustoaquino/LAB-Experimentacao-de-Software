import React, { useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from 'recharts';

const dadosPorRepo = [
  { repositorio: "angular/angular", tratamento: "GraphQL", tempo_medio: 633.41, tamanho_medio: 925.0 },
  { repositorio: "angular/angular", tratamento: "REST", tempo_medio: 1373.83, tamanho_medio: 33888.1 },
  { repositorio: "django/django", tratamento: "GraphQL", tempo_medio: 628.96, tamanho_medio: 209.0 },
  { repositorio: "django/django", tratamento: "REST", tempo_medio: 1341.39, tamanho_medio: 25854.0 },
  { repositorio: "facebook/react", tratamento: "GraphQL", tempo_medio: 641.55, tamanho_medio: 801.0 },
  { repositorio: "facebook/react", tratamento: "REST", tempo_medio: 1754.44, tamanho_medio: 20350.0 },
  { repositorio: "microsoft/vscode", tratamento: "GraphQL", tempo_medio: 689.11, tamanho_medio: 766.0 },
  { repositorio: "microsoft/vscode", tratamento: "REST", tempo_medio: 1470.2, tamanho_medio: 35387.48 },
  { repositorio: "nodejs/node", tratamento: "GraphQL", tempo_medio: 660.71, tamanho_medio: 835.0 },
  { repositorio: "nodejs/node", tratamento: "REST", tempo_medio: 1386.23, tamanho_medio: 39266.0 },
  { repositorio: "pytorch/pytorch", tratamento: "GraphQL", tempo_medio: 638.13, tamanho_medio: 1020.0 },
  { repositorio: "pytorch/pytorch", tratamento: "REST", tempo_medio: 1444.47, tamanho_medio: 53174.9 },
  { repositorio: "rails/rails", tratamento: "GraphQL", tempo_medio: 622.37, tamanho_medio: 936.0 },
  { repositorio: "rails/rails", tratamento: "REST", tempo_medio: 1319.41, tamanho_medio: 24334.0 },
  { repositorio: "tensorflow/tensorflow", tratamento: "GraphQL", tempo_medio: 679.37, tamanho_medio: 1006.0 },
  { repositorio: "tensorflow/tensorflow", tratamento: "REST", tempo_medio: 1427.06, tamanho_medio: 24372.0 },
  { repositorio: "torvalds/linux", tratamento: "GraphQL", tempo_medio: 567.82, tamanho_medio: 176.0 },
  { repositorio: "torvalds/linux", tratamento: "REST", tempo_medio: 1236.83, tamanho_medio: 5081.0 },
  { repositorio: "vuejs/vue", tratamento: "GraphQL", tempo_medio: 610.29, tamanho_medio: 990.0 },
  { repositorio: "vuejs/vue", tratamento: "REST", tempo_medio: 1321.66, tamanho_medio: 25091.0 },
];

const descritivas = {
  REST: { tempo: { media: 1382.98, mediana: 1365.72, dp: 159.50, n: 276 }, tamanho: { media: 29370.51, mediana: 25854.00, dp: 12394.72, n: 276 } },
  GraphQL: { tempo: { media: 636.99, mediana: 634.80, dp: 80.21, n: 295 }, tamanho: { media: 764.77, mediana: 925.00, dp: 300.92, n: 295 } },
};

const testes = [
  { rq: "RQ1", metrica: "Tempo de Resposta", teste: "teste de Wilcoxon pareado (não-paramétrico)", estatistica: 0.00, p: "< 0,001", diff: "724,30 ms", significativo: true },
  { rq: "RQ2", metrica: "Tamanho da Resposta", teste: "teste de Wilcoxon pareado (não-paramétrico)", estatistica: 0.00, p: "< 0,001", diff: "25.645 bytes", significativo: true },
];

const CORES = { REST: "#4C72B0", GraphQL: "#DD8452" };

function pivot(metricKey) {
  const repos = [...new Set(dadosPorRepo.map(d => d.repositorio))];
  return repos.map(repo => {
    const rest = dadosPorRepo.find(d => d.repositorio === repo && d.tratamento === "REST");
    const gql = dadosPorRepo.find(d => d.repositorio === repo && d.tratamento === "GraphQL");
    return {
      repositorio: repo.includes('/') ? repo.split('/')[1] : repo,
      REST: rest ? rest[metricKey] : 0,
      GraphQL: gql ? gql[metricKey] : 0,
    };
  });
}

function StatCard({ label, rest, graphql, unit, decimals = 2 }) {
  const reducaoPct = (((rest - graphql) / rest) * 100).toFixed(1);
  const melhor = graphql < rest ? 'GraphQL' : 'REST';
  return (
    <div style={{ background: '#fff', borderRadius: 12, padding: '20px 24px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)', flex: 1, minWidth: 220 }}>
      <div style={{ fontSize: 13, color: '#8a8a8a', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 12 }}>{label}</div>
      <div style={{ display: 'flex', gap: 24, marginBottom: 10 }}>
        <div>
          <div style={{ fontSize: 12, color: CORES.REST, fontWeight: 600 }}>REST</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: '#1f2937' }}>{rest.toLocaleString('pt-BR', { maximumFractionDigits: decimals })}{unit}</div>
        </div>
        <div>
          <div style={{ fontSize: 12, color: CORES.GraphQL, fontWeight: 600 }}>GraphQL</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: '#1f2937' }}>{graphql.toLocaleString('pt-BR', { maximumFractionDigits: decimals })}{unit}</div>
        </div>
      </div>
      <div style={{ fontSize: 13, color: '#059669', fontWeight: 600, background: '#ecfdf5', display: 'inline-block', padding: '4px 10px', borderRadius: 6 }}>
        {reducaoPct > 0 ? '↓' : '↑'} {Math.abs(reducaoPct)}% com {melhor}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [metrica, setMetrica] = useState('tempo');

  const metricKey = metrica === 'tempo' ? 'tempo_medio' : 'tamanho_medio';
  const dadosGrafico = pivot(metricKey);
  const unidade = metrica === 'tempo' ? ' ms' : ' B';

  return (
    <div style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', background: '#f4f5f7', minHeight: '100vh', padding: 24 }}>
      <div style={{ maxWidth: 1100, margin: '0 auto' }}>

        <div style={{ marginBottom: 24 }}>
          <h1 style={{ fontSize: 26, fontWeight: 800, color: '#1f2937', margin: 0 }}>GraphQL vs REST — Dashboard de Resultados</h1>
          <p style={{ color: '#6b7280', marginTop: 6, fontSize: 14 }}>
            Experimento controlado · API do GitHub · 10 repositórios · 600 medições brutas coletadas
          </p>
        </div>

        <div style={{ display: 'flex', gap: 16, marginBottom: 24, flexWrap: 'wrap' }}>
          <StatCard label="Tempo de Resposta (média)" rest={descritivas.REST.tempo.media} graphql={descritivas.GraphQL.tempo.media} unit=" ms" />
          <StatCard label="Tamanho da Resposta (média)" rest={descritivas.REST.tamanho.media} graphql={descritivas.GraphQL.tamanho.media} unit=" B" decimals={0} />
        </div>

        <div style={{ background: '#fff', borderRadius: 12, padding: 20, boxShadow: '0 1px 3px rgba(0,0,0,0.08)', marginBottom: 24 }}>
          <div style={{ fontSize: 13, color: '#8a8a8a', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 14 }}>
            Testes de Hipótese (α = 0,05)
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            {testes.map(t => (
              <div key={t.rq} style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 14 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <span style={{ fontWeight: 700, color: '#1f2937' }}>{t.rq} — {t.metrica}</span>
                  <span style={{ fontSize: 12, fontWeight: 700, color: t.significativo ? '#059669' : '#dc2626', background: t.significativo ? '#ecfdf5' : '#fef2f2', padding: '3px 8px', borderRadius: 6 }}>
                    {t.significativo ? 'SIGNIFICATIVO' : 'NÃO SIGNIFICATIVO'}
                  </span>
                </div>
                <div style={{ fontSize: 13, color: '#6b7280', lineHeight: 1.6 }}>
                  Teste: {t.teste}<br/>
                  Estatística: {t.estatistica} · p-valor: {t.p}<br/>
                  Diferença mediana (REST − GraphQL): <strong>{t.diff}</strong>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
          {['tempo', 'tamanho'].map(m => (
            <button
              key={m}
              onClick={() => setMetrica(m)}
              style={{
                padding: '8px 16px', borderRadius: 8, border: 'none', cursor: 'pointer',
                fontWeight: 600, fontSize: 13,
                background: metrica === m ? '#1f2937' : '#fff',
                color: metrica === m ? '#fff' : '#6b7280',
                boxShadow: '0 1px 2px rgba(0,0,0,0.06)'
              }}
            >
              {m === 'tempo' ? 'Tempo de Resposta' : 'Tamanho da Resposta'}
            </button>
          ))}
        </div>

        <div style={{ background: '#fff', borderRadius: 12, padding: 20, boxShadow: '0 1px 3px rgba(0,0,0,0.08)', marginBottom: 24 }}>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#1f2937', marginBottom: 16 }}>
            {metrica === 'tempo' ? 'Tempo Médio de Resposta por Repositório' : 'Tamanho Médio de Resposta por Repositório'}
          </div>
          <ResponsiveContainer width="100%" height={360}>
            <BarChart data={dadosGrafico} margin={{ top: 10, right: 10, left: 0, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
              <XAxis dataKey="repositorio" angle={-35} textAnchor="end" interval={0} tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} label={{ value: metrica === 'tempo' ? 'ms' : 'bytes', angle: -90, position: 'insideLeft', fontSize: 12 }} />
              <Tooltip formatter={(v) => v.toLocaleString('pt-BR', { maximumFractionDigits: 1 }) + unidade} />
              <Legend />
              <Bar dataKey="REST" fill={CORES.REST} radius={[4, 4, 0, 0]} />
              <Bar dataKey="GraphQL" fill={CORES.GraphQL} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div style={{ fontSize: 12, color: '#9ca3af', textAlign: 'center', paddingBottom: 12 }}>
          LAB05 · Laboratório de Experimentação de Software · PUC Minas
        </div>
      </div>
    </div>
  );
}
