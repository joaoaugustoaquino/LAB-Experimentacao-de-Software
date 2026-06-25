import os
import json
import pandas as pd
import scipy.stats as stats

BASE = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(BASE, "data")

# ---------------------------------------------------------------------------
# 1. Carrega os dados reais
# ---------------------------------------------------------------------------

df = pd.read_csv(os.path.join(DATA_DIR, "resultados_limpos.csv"))
desc = pd.read_csv(os.path.join(DATA_DIR, "estatisticas_descritivas.csv"))
testes = pd.read_csv(os.path.join(DATA_DIR, "testes_hipotese.csv"))


def get_desc(tratamento, metrica_label):
    row = desc[(desc["tratamento"] == tratamento) & (desc["metrica"] == metrica_label)].iloc[0]
    return row


desc_rest_tempo = get_desc("REST", "Tempo de Resposta (ms)")
desc_gql_tempo = get_desc("GraphQL", "Tempo de Resposta (ms)")
desc_rest_tam = get_desc("REST", "Tamanho da Resposta (bytes)")
desc_gql_tam = get_desc("GraphQL", "Tamanho da Resposta (bytes)")

teste_rq1 = testes[testes["RQ"] == "RQ1"].iloc[0]
teste_rq2 = testes[testes["RQ"] == "RQ2"].iloc[0]


def fmt_br(valor, decimais=2):
    """Formata número no padrão brasileiro: 1.234,56"""
    s = f"{valor:,.{decimais}f}"
    s = s.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
    return s


def fmt_p(p):
    if p < 0.001:
        return "< 0,001"
    return fmt_br(p, 3)


def normalidade_resultado():
    """Recalcula se ambos os grupos passaram no Shapiro-Wilk para descrever no texto."""
    resultados = {}
    for trat in ["REST", "GraphQL"]:
        for metrica in ["tempo_resposta_ms", "tamanho_resposta_bytes"]:
            valores = df[df["tratamento"] == trat][metrica]
            _, p = stats.shapiro(valores)
            resultados[(trat, metrica)] = p
    return resultados


norm = normalidade_resultado()
ambos_normais_tempo = norm[("REST", "tempo_resposta_ms")] > 0.05 and norm[("GraphQL", "tempo_resposta_ms")] > 0.05
texto_teste_usado = (
    "teste t de Student pareado" if ambos_normais_tempo else
    "teste de Wilcoxon pareado (não-paramétrico)"
)
texto_normalidade = (
    "Como ambos os grupos apresentaram distribuição compatível com normalidade (p > 0,05), "
    "foi utilizado o teste t de Student pareado para comparar as médias de cada métrica entre "
    "os tratamentos, ao nível de significância de 5% (α = 0,05)."
    if ambos_normais_tempo else
    "Como ao menos um dos grupos não apresentou distribuição compatível com normalidade "
    "(p ≤ 0,05 no teste de Shapiro-Wilk), foi utilizado o teste de Wilcoxon pareado "
    "(não-paramétrico) para comparar as métricas entre os tratamentos, ao nível de "
    "significância de 5% (α = 0,05)."
)

n_repos = df["repositorio"].nunique()
n_total_bruto = len(pd.read_csv(os.path.join(DATA_DIR, "resultados_brutos.csv")))
n_rest = int(desc_rest_tempo["n"])
n_gql = int(desc_gql_tempo["n"])

resultado_rq1_significativo = bool(teste_rq1["significativo_5pct"])
resultado_rq2_significativo = bool(teste_rq2["significativo_5pct"])

quem_mais_rapido = "GraphQL" if desc_gql_tempo["media"] < desc_rest_tempo["media"] else "REST"
quem_menor_payload = "GraphQL" if desc_gql_tam["media"] < desc_rest_tam["media"] else "REST"

# ---------------------------------------------------------------------------
# 2. Monta tabela agregada por repositório (para o dashboard)
# ---------------------------------------------------------------------------

agg = (
    df.groupby(["repositorio", "tratamento"])
    .agg(tempo_medio=("tempo_resposta_ms", "mean"), tamanho_medio=("tamanho_resposta_bytes", "mean"))
    .reset_index()
)
agg["tempo_medio"] = agg["tempo_medio"].round(2)
agg["tamanho_medio"] = agg["tamanho_medio"].round(2)
dados_por_repo_js = agg.to_dict(orient="records")

# ---------------------------------------------------------------------------
# 3. Gera scripts/gerar_relatorio.js
# ---------------------------------------------------------------------------

GRAF = os.path.join(BASE, "graficos").replace("\\", "/")

relatorio_js = f"""const {{ Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        ImageRun, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
        WidthType, ShadingType, PageNumber, Footer, Header }} = require('docx');
const fs = require('fs');

const GRAF = '{GRAF}';

function imgBuf(path) {{ return fs.readFileSync(path); }}

const border = {{ style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" }};
const borders = {{ top: border, bottom: border, left: border, right: border }};

function headerCell(text, width) {{
  return new TableCell({{
    borders,
    width: {{ size: width, type: WidthType.DXA }},
    shading: {{ fill: "2E5C8A", type: ShadingType.CLEAR }},
    margins: {{ top: 80, bottom: 80, left: 120, right: 120 }},
    children: [new Paragraph({{ children: [new TextRun({{ text, bold: true, color: "FFFFFF" }})] }})]
  }});
}}

function cell(text, width) {{
  return new TableCell({{
    borders,
    width: {{ size: width, type: WidthType.DXA }},
    margins: {{ top: 80, bottom: 80, left: 120, right: 120 }},
    children: [new Paragraph({{ children: [new TextRun(text)] }})]
  }});
}}

const doc = new Document({{
  styles: {{
    default: {{ document: {{ run: {{ font: "Arial", size: 22 }} }} }},
    paragraphStyles: [
      {{ id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: {{ size: 32, bold: true, font: "Arial", color: "1F3864" }},
        paragraph: {{ spacing: {{ before: 320, after: 200 }}, outlineLevel: 0 }} }},
      {{ id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: {{ size: 26, bold: true, font: "Arial", color: "2E5C8A" }},
        paragraph: {{ spacing: {{ before: 260, after: 160 }}, outlineLevel: 1 }} }},
      {{ id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: {{ size: 24, bold: true, font: "Arial", color: "2E5C8A" }},
        paragraph: {{ spacing: {{ before: 200, after: 120 }}, outlineLevel: 2 }} }},
    ]
  }},
  numbering: {{
    config: [
      {{ reference: "bullets", levels: [{{ level: 0, format: LevelFormat.BULLET, text: "\\u2022",
        alignment: AlignmentType.LEFT, style: {{ paragraph: {{ indent: {{ left: 720, hanging: 360 }} }} }} }}] }},
      {{ reference: "numbers", levels: [{{ level: 0, format: LevelFormat.DECIMAL, text: "%1.",
        alignment: AlignmentType.LEFT, style: {{ paragraph: {{ indent: {{ left: 720, hanging: 360 }} }} }} }}] }},
    ]
  }},
  sections: [{{
    properties: {{
      page: {{ size: {{ width: 12240, height: 15840 }}, margin: {{ top: 1440, right: 1440, bottom: 1440, left: 1440 }} }}
    }},
    headers: {{
      default: new Header({{ children: [new Paragraph({{
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({{ text: "LAB05 \u2014 GraphQL vs REST", size: 18, color: "888888" }})]
      }})] }})
    }},
    footers: {{
      default: new Footer({{ children: [new Paragraph({{
        alignment: AlignmentType.CENTER,
        children: [new TextRun({{ text: "P\u00e1gina ", size: 18, color: "888888" }}),
                    new TextRun({{ children: [PageNumber.CURRENT], size: 18, color: "888888" }})]
      }})] }})
    }},
    children: [
      new Paragraph({{
        alignment: AlignmentType.CENTER,
        spacing: {{ after: 80 }},
        children: [new TextRun({{ text: "GraphQL vs REST", bold: true, size: 44, color: "1F3864" }})]
      }}),
      new Paragraph({{
        alignment: AlignmentType.CENTER,
        spacing: {{ after: 40 }},
        children: [new TextRun({{ text: "Um Experimento Controlado", size: 28, color: "2E5C8A" }})]
      }}),
      new Paragraph({{
        alignment: AlignmentType.CENTER,
        spacing: {{ after: 400 }},
        children: [new TextRun({{ text: "Laborat\u00f3rio de Experimenta\u00e7\u00e3o de Software \u2014 PUC Minas", size: 20, italics: true, color: "666666" }})]
      }}),

      new Paragraph({{ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Introdu\u00e7\u00e3o")] }}),
      new Paragraph({{
        spacing: {{ after: 160 }},
        children: [new TextRun(
          "GraphQL \u00e9 uma linguagem de consulta para APIs Web, proposta pelo Facebook, baseada em " +
          "grafos e schemas definidos pelo servidor, permitindo que o cliente especifique exatamente " +
          "quais campos deseja obter em uma \u00fanica requisi\u00e7\u00e3o. Em contraste, APIs REST organizam-se em " +
          "torno de endpoints fixos, frequentemente retornando estruturas de dados predefinidas que podem " +
          "conter mais informa\u00e7\u00e3o do que o cliente necessita (overfetching) ou exigir m\u00faltiplas chamadas " +
          "para compor a informa\u00e7\u00e3o desejada (underfetching)."
        )]
      }}),
      new Paragraph({{
        spacing: {{ after: 160 }},
        children: [new TextRun(
          "Este relat\u00f3rio descreve um experimento controlado, com desenho pareado (within-subject), " +
          "comparando o desempenho de consultas equivalentes realizadas via API REST e API GraphQL do " +
          "GitHub, com o objetivo de responder quantitativamente \u00e0s seguintes perguntas de pesquisa:"
        )]
      }}),
      new Paragraph({{ numbering: {{ reference: "numbers", level: 0 }}, spacing: {{ after: 80 }},
        children: [new TextRun({{ text: "RQ1: ", bold: true }}), new TextRun("Respostas \u00e0s consultas GraphQL s\u00e3o mais r\u00e1pidas que respostas \u00e0s consultas REST?")] }}),
      new Paragraph({{ numbering: {{ reference: "numbers", level: 0 }}, spacing: {{ after: 200 }},
        children: [new TextRun({{ text: "RQ2: ", bold: true }}), new TextRun("Respostas \u00e0s consultas GraphQL t\u00eam tamanho menor que respostas \u00e0s consultas REST?")] }}),

      new Paragraph({{ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.1 Hip\u00f3teses")] }}),
      new Paragraph({{ spacing: {{ after: 60 }}, children: [new TextRun({{ text: "Para RQ1 (tempo de resposta):", bold: true }})] }}),
      new Paragraph({{ numbering: {{ reference: "bullets", level: 0 }}, children: [new TextRun("H0\u2081: n\u00e3o h\u00e1 diferen\u00e7a significativa no tempo de resposta entre GraphQL e REST.")] }}),
      new Paragraph({{ numbering: {{ reference: "bullets", level: 0 }}, spacing: {{ after: 160 }}, children: [new TextRun("H1\u2081: existe diferen\u00e7a significativa no tempo de resposta entre GraphQL e REST.")] }}),
      new Paragraph({{ spacing: {{ after: 60 }}, children: [new TextRun({{ text: "Para RQ2 (tamanho de resposta):", bold: true }})] }}),
      new Paragraph({{ numbering: {{ reference: "bullets", level: 0 }}, children: [new TextRun("H0\u2082: n\u00e3o h\u00e1 diferen\u00e7a significativa no tamanho de resposta entre GraphQL e REST.")] }}),
      new Paragraph({{ numbering: {{ reference: "bullets", level: 0 }}, spacing: {{ after: 160 }}, children: [new TextRun("H1\u2082: existe diferen\u00e7a significativa no tamanho de resposta entre GraphQL e REST.")] }}),

      new Paragraph({{ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Metodologia")] }}),

      new Paragraph({{ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 Vari\u00e1veis")] }}),
      new Paragraph({{ children: [new TextRun({{ text: "Vari\u00e1vel independente: ", bold: true }}), new TextRun("tipo de API utilizada (REST ou GraphQL), categ\u00f3rica com 2 n\u00edveis.")] }}),
      new Paragraph({{ spacing: {{ after: 160 }}, children: [new TextRun({{ text: "Vari\u00e1veis dependentes: ", bold: true }}), new TextRun("(i) tempo de resposta, em milissegundos; (ii) tamanho da resposta, em bytes.")] }}),

      new Paragraph({{ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 Tratamentos e Objetos Experimentais")] }}),
      new Paragraph({{ spacing: {{ after: 160 }}, children: [new TextRun(
        "Foram definidos dois tratamentos: (T1) consulta via API REST do GitHub e (T2) consulta " +
        "equivalente via API GraphQL do GitHub. Os objetos experimentais consistem em {n_repos} repositórios " +
        "públicos (mesmo conjunto utilizado nos dois tratamentos), consultados para os mesmos dados: nome, " +
        "descrição, número de estrelas, número de forks, linguagem principal e as 5 issues abertas mais recentes."
      )]}}),

      new Paragraph({{ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.3 Tipo de Projeto Experimental")] }}),
      new Paragraph({{ spacing: {{ after: 160 }}, children: [new TextRun(
        "Foi adotado um desenho pareado (within-subject / paired design): cada repositório foi consultado " +
        "por ambos os tratamentos, controlando a variação entre objetos experimentais e aumentando o poder " +
        "estatístico do teste de hipótese, já que cada par de observações compartilha o mesmo objeto."
      )]}}),

      new Paragraph({{ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.4 Quantidade de Medições")] }}),
      new Paragraph({{ spacing: {{ after: 160 }}, children: [new TextRun(
        "Foram coletadas {n_total_bruto} medições brutas, das quais {n_rest} (tratamento REST) e {n_gql} " +
        "(tratamento GraphQL) permaneceram após validação e remoção de outliers via IQR. A ordem de " +
        "execução dos tratamentos e dos repositórios foi aleatorizada a cada repetição, de modo a mitigar " +
        "efeitos de hora do dia, cache e variação de rede."
      )]}}),

      new Paragraph({{ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.5 Ambiente e Reprodutibilidade")] }}),
      new Paragraph({{ spacing: {{ after: 80 }}, children: [new TextRun(
        "O experimento foi implementado em Python 3.12, utilizando a biblioteca requests para realizar " +
        "as chamadas HTTP. As medições de tempo foram feitas com time.perf_counter(), capturando o " +
        "intervalo entre o início da requisição e o recebimento completo da resposta. O tamanho da " +
        "resposta foi obtido a partir do corpo (body) retornado pela API, em bytes."
      )]}}),
      new Paragraph({{ spacing: {{ after: 80 }}, children: [new TextRun(
        "Para a API REST, como não existe um único endpoint que combine dados do repositório e issues, " +
        "a medição de cada trial soma o tempo e o tamanho de duas chamadas: GET /repos/{{owner}}/{{repo}} e " +
        "GET /repos/{{owner}}/{{repo}}/issues. Para a API GraphQL, uma única consulta (query) equivalente " +
        "retorna o mesmo conjunto de dados em uma única chamada POST."
      )]}}),
      new Paragraph({{ spacing: {{ after: 160 }}, children: [new TextRun(
        "Os scripts de coleta (coletar_dados.py), análise estatística (analisar_dados.py) e geração de " +
        "gráficos (gerar_graficos.py) estão disponíveis no pacote de arquivos deste laboratório, permitindo " +
        "a reprodução integral do experimento mediante um GitHub Personal Access Token válido."
      )]}}),

      new Paragraph({{ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.6 Análise Estatística")] }}),
      new Paragraph({{ spacing: {{ after: 160 }}, children: [new TextRun(
        "Após a coleta, os dados passaram por validação (remoção de medições com falha) e remoção de " +
        "outliers via método IQR (intervalo interquartil) por tratamento. Em seguida, foi aplicado o " +
        "teste de Shapiro-Wilk para verificar normalidade das distribuições. {texto_normalidade}"
      )]}}),

      new Paragraph({{ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.7 Ameaças à Validade")] }}),
      new Paragraph({{ numbering: {{ reference: "bullets", level: 0 }}, children: [new TextRun({{ text: "Validade interna: ", bold: true }}), new TextRun("variações de latência de rede e cache durante a coleta foram mitigadas por meio de aleatorização da ordem de execução e múltiplas repetições.")] }}),
      new Paragraph({{ numbering: {{ reference: "bullets", level: 0 }}, children: [new TextRun({{ text: "Validade externa: ", bold: true }}), new TextRun("os resultados refletem o comportamento específico da API do GitHub, podendo não generalizar diretamente para outras APIs ou domínios.")] }}),
      new Paragraph({{ numbering: {{ reference: "bullets", level: 0 }}, children: [new TextRun({{ text: "Validade de construto: ", bold: true }}), new TextRun("o tempo medido no cliente inclui latência de rede, não isolando apenas o tempo de processamento no servidor.")] }}),
      new Paragraph({{ numbering: {{ reference: "bullets", level: 0 }}, spacing: {{ after: 160 }}, children: [new TextRun({{ text: "Validade de conclusão: ", bold: true }}), new TextRun("o tamanho amostral e os testes estatísticos apropriados reduzem o risco de conclusões espúrias.")] }}),

      new Paragraph({{ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. Resultados")] }}),

      new Paragraph({{ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 Estatística Descritiva")] }}),
      new Paragraph({{ spacing: {{ after: 160 }}, children: [new TextRun(
        "A Tabela 1 apresenta as estatísticas descritivas das medições válidas (após remoção de " +
        "outliers) para cada tratamento e métrica."
      )]}}),

      new Table({{
        width: {{ size: 9360, type: WidthType.DXA }},
        columnWidths: [2200, 1700, 1500, 1700, 1130, 1130],
        rows: [
          new TableRow({{ children: [
            headerCell("Métrica", 2200), headerCell("Tratamento", 1700), headerCell("Média", 1500),
            headerCell("Mediana", 1700), headerCell("Desvio Padrão", 1130), headerCell("n", 1130)
          ]}}),
          new TableRow({{ children: [
            cell("Tempo de Resposta (ms)", 2200), cell("REST", 1700), cell("{fmt_br(desc_rest_tempo['media'])}", 1500),
            cell("{fmt_br(desc_rest_tempo['mediana'])}", 1700), cell("{fmt_br(desc_rest_tempo['desvio_padrao'])}", 1130), cell("{n_rest}", 1130)
          ]}}),
          new TableRow({{ children: [
            cell("Tempo de Resposta (ms)", 2200), cell("GraphQL", 1700), cell("{fmt_br(desc_gql_tempo['media'])}", 1500),
            cell("{fmt_br(desc_gql_tempo['mediana'])}", 1700), cell("{fmt_br(desc_gql_tempo['desvio_padrao'])}", 1130), cell("{n_gql}", 1130)
          ]}}),
          new TableRow({{ children: [
            cell("Tamanho da Resposta (bytes)", 2200), cell("REST", 1700), cell("{fmt_br(desc_rest_tam['media'], 0)}", 1500),
            cell("{fmt_br(desc_rest_tam['mediana'], 0)}", 1700), cell("{fmt_br(desc_rest_tam['desvio_padrao'], 0)}", 1130), cell("{n_rest}", 1130)
          ]}}),
          new TableRow({{ children: [
            cell("Tamanho da Resposta (bytes)", 2200), cell("GraphQL", 1700), cell("{fmt_br(desc_gql_tam['media'], 0)}", 1500),
            cell("{fmt_br(desc_gql_tam['mediana'], 0)}", 1700), cell("{fmt_br(desc_gql_tam['desvio_padrao'], 0)}", 1130), cell("{n_gql}", 1130)
          ]}}),
        ]
      }}),
      new Paragraph({{ spacing: {{ before: 80, after: 240 }}, children: [new TextRun({{ text: "Tabela 1. ", italics: true, bold: true }}), new TextRun({{ text: "Estatísticas descritivas por tratamento e métrica.", italics: true, size: 20 }})] }}),

      new Paragraph({{ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 RQ1 — Tempo de Resposta")] }}),
      new Paragraph({{ spacing: {{ after: 160 }}, children: [new TextRun(
        "O {texto_teste_usado} indicou {'diferença estatisticamente significativa' if resultado_rq1_significativo else 'que NÃO há diferença estatisticamente significativa'} entre os " +
        "tratamentos (estatística = {fmt_br(abs(teste_rq1['estatistica']))}; p-valor {fmt_p(teste_rq1['p_valor'])}). A diferença mediana observada foi de aproximadamente " +
        "{fmt_br(abs(teste_rq1['diferenca_mediana_REST_menos_GraphQL']))} ms, com {quem_mais_rapido} apresentando tempos de resposta menores. " +
        "Dessa forma, H0₁ é {'rejeitada em favor de H1₁' if resultado_rq1_significativo else 'mantida'}."
      )]}}),
      new Paragraph({{
        children: [new ImageRun({{ data: imgBuf(`${{GRAF}}/boxplot_tempo.png`), transformation: {{ width: 500, height: 357 }}, type: "png" }})],
        alignment: AlignmentType.CENTER
      }}),
      new Paragraph({{ alignment: AlignmentType.CENTER, spacing: {{ before: 80, after: 240 }}, children: [new TextRun({{ text: "Figura 1. Distribuição do tempo de resposta por tratamento.", italics: true, size: 20 }})] }}),

      new Paragraph({{ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.3 RQ2 — Tamanho da Resposta")] }}),
      new Paragraph({{ spacing: {{ after: 160 }}, children: [new TextRun(
        "O {texto_teste_usado} indicou {'diferença estatisticamente significativa' if resultado_rq2_significativo else 'que NÃO há diferença estatisticamente significativa'} entre os " +
        "tratamentos (estatística = {fmt_br(abs(teste_rq2['estatistica']))}; p-valor {fmt_p(teste_rq2['p_valor'])}). A diferença mediana foi de aproximadamente " +
        "{fmt_br(abs(teste_rq2['diferenca_mediana_REST_menos_GraphQL']), 0)} bytes, com as respostas {quem_menor_payload} sendo menores. " +
        "Dessa forma, H0₂ é {'rejeitada em favor de H1₂' if resultado_rq2_significativo else 'mantida'}."
      )]}}),
      new Paragraph({{
        children: [new ImageRun({{ data: imgBuf(`${{GRAF}}/boxplot_tamanho.png`), transformation: {{ width: 500, height: 357 }}, type: "png" }})],
        alignment: AlignmentType.CENTER
      }}),
      new Paragraph({{ alignment: AlignmentType.CENTER, spacing: {{ before: 80, after: 240 }}, children: [new TextRun({{ text: "Figura 2. Distribuição do tamanho da resposta por tratamento.", italics: true, size: 20 }})] }}),

      new Paragraph({{ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.4 Comparação por Repositório")] }}),
      new Paragraph({{
        children: [new ImageRun({{ data: imgBuf(`${{GRAF}}/barras_media_por_repositorio_tamanho.png`), transformation: {{ width: 580, height: 348 }}, type: "png" }})],
        alignment: AlignmentType.CENTER
      }}),
      new Paragraph({{ alignment: AlignmentType.CENTER, spacing: {{ before: 80, after: 240 }}, children: [new TextRun({{ text: "Figura 3. Tamanho médio da resposta por repositório e tratamento.", italics: true, size: 20 }})] }}),

      new Paragraph({{ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Discussão")] }}),
      new Paragraph({{ spacing: {{ after: 160 }}, children: [new TextRun(
        "Os resultados deste experimento controlado {'fornecem evidência estatística' if (resultado_rq1_significativo or resultado_rq2_significativo) else 'não fornecem evidência estatística suficiente'} de que, " +
        "no contexto da API do GitHub e para o conjunto de consultas avaliado, {quem_mais_rapido} apresenta respostas " +
        "mais rápidas e {quem_menor_payload} apresenta respostas menores que a outra abordagem, respondendo a " +
        "RQ1 ({'sim' if resultado_rq1_significativo else 'sem evidência suficiente'}) e RQ2 ({'sim' if resultado_rq2_significativo else 'sem evidência suficiente'})."
      )]}}),
      new Paragraph({{ spacing: {{ after: 160 }}, children: [new TextRun(
        "A diferença no tamanho da resposta é consistente com a principal vantagem teórica do GraphQL: a " +
        "eliminação de overfetching, já que o cliente especifica exatamente os campos desejados, ao invés " +
        "de receber a estrutura completa predefinida pelo endpoint REST. A diferença no tempo de resposta, " +
        "por sua vez, pode ser parcialmente explicada pela necessidade de duas chamadas HTTP separadas no " +
        "tratamento REST (uma para dados do repositório e outra para issues), enquanto o GraphQL resolveu a " +
        "mesma necessidade em uma única requisição."
      )]}}),
      new Paragraph({{ spacing: {{ after: 160 }}, children: [new TextRun(
        "É importante notar que essa vantagem pode não se generalizar para todos os cenários: em consultas " +
        "mais simples, que já mapeiam para um único endpoint REST, a diferença de tempo poderia ser menor " +
        "ou mesmo inexistente, já que o servidor GraphQL incorre em overhead adicional de resolução de " +
        "schema. O ganho mais robusto e generalizável observado neste experimento é o de tamanho de " +
        "payload, diretamente relacionado à quantidade de dados transferidos pela rede."
      )]}}),
      new Paragraph({{ spacing: {{ after: 160 }}, children: [new TextRun(
        "Como trabalhos futuros, seria relevante repetir o experimento variando a complexidade das " +
        "consultas (campos aninhados, profundidade do grafo) e comparando diferentes provedores de API, " +
        "de modo a avaliar a robustez externa dessas conclusões."
      )]}}),
    ]
  }}]
}});

Packer.toBuffer(doc).then(buffer => {{
  fs.writeFileSync('{os.path.join(BASE, "relatorio", "Relatorio_Final_LAB05.docx").replace(chr(92), "/")}', buffer);
  console.log('Relatório gerado com sucesso com os dados reais.');
}});
"""

os.makedirs(os.path.join(BASE, "scripts"), exist_ok=True)
with open(os.path.join(BASE, "scripts", "gerar_relatorio.js"), "w", encoding="utf-8") as f:
    f.write(relatorio_js)

print("scripts/gerar_relatorio.js atualizado com os números reais.")

# ---------------------------------------------------------------------------
# 4. Gera dashboard.jsx
# ---------------------------------------------------------------------------

dados_por_repo_str = json.dumps(dados_por_repo_js, ensure_ascii=False, indent=2)
dados_por_repo_str = dados_por_repo_str.replace('"repositorio"', "repositorio:" ).replace('"tratamento"', "tratamento:").replace('"tempo_medio"', "tempo_medio:").replace('"tamanho_medio"', "tamanho_medio:")
# Simpler: just rebuild manually as JS literal to avoid quoting headaches
linhas_js = []
for row in dados_por_repo_js:
    linhas_js.append(
        f'  {{ repositorio: "{row["repositorio"]}", tratamento: "{row["tratamento"]}", '
        f'tempo_medio: {row["tempo_medio"]}, tamanho_medio: {row["tamanho_medio"]} }},'
    )
dados_por_repo_js_literal = "\n".join(linhas_js)

dashboard_jsx = f"""import React, {{ useState }} from 'react';
import {{
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
}} from 'recharts';

const dadosPorRepo = [
{dados_por_repo_js_literal}
];

const descritivas = {{
  REST: {{ tempo: {{ media: {desc_rest_tempo['media']:.2f}, mediana: {desc_rest_tempo['mediana']:.2f}, dp: {desc_rest_tempo['desvio_padrao']:.2f}, n: {n_rest} }}, tamanho: {{ media: {desc_rest_tam['media']:.2f}, mediana: {desc_rest_tam['mediana']:.2f}, dp: {desc_rest_tam['desvio_padrao']:.2f}, n: {n_rest} }} }},
  GraphQL: {{ tempo: {{ media: {desc_gql_tempo['media']:.2f}, mediana: {desc_gql_tempo['mediana']:.2f}, dp: {desc_gql_tempo['desvio_padrao']:.2f}, n: {n_gql} }}, tamanho: {{ media: {desc_gql_tam['media']:.2f}, mediana: {desc_gql_tam['mediana']:.2f}, dp: {desc_gql_tam['desvio_padrao']:.2f}, n: {n_gql} }} }},
}};

const testes = [
  {{ rq: "RQ1", metrica: "Tempo de Resposta", teste: "{texto_teste_usado}", estatistica: {abs(teste_rq1['estatistica']):.2f}, p: "{fmt_p(teste_rq1['p_valor'])}", diff: "{fmt_br(abs(teste_rq1['diferenca_mediana_REST_menos_GraphQL']))} ms", significativo: {str(resultado_rq1_significativo).lower()} }},
  {{ rq: "RQ2", metrica: "Tamanho da Resposta", teste: "{texto_teste_usado}", estatistica: {abs(teste_rq2['estatistica']):.2f}, p: "{fmt_p(teste_rq2['p_valor'])}", diff: "{fmt_br(abs(teste_rq2['diferenca_mediana_REST_menos_GraphQL']), 0)} bytes", significativo: {str(resultado_rq2_significativo).lower()} }},
];

const CORES = {{ REST: "#4C72B0", GraphQL: "#DD8452" }};

function pivot(metricKey) {{
  const repos = [...new Set(dadosPorRepo.map(d => d.repositorio))];
  return repos.map(repo => {{
    const rest = dadosPorRepo.find(d => d.repositorio === repo && d.tratamento === "REST");
    const gql = dadosPorRepo.find(d => d.repositorio === repo && d.tratamento === "GraphQL");
    return {{
      repositorio: repo.includes('/') ? repo.split('/')[1] : repo,
      REST: rest ? rest[metricKey] : 0,
      GraphQL: gql ? gql[metricKey] : 0,
    }};
  }});
}}

function StatCard({{ label, rest, graphql, unit, decimals = 2 }}) {{
  const reducaoPct = (((rest - graphql) / rest) * 100).toFixed(1);
  const melhor = graphql < rest ? 'GraphQL' : 'REST';
  return (
    <div style={{{{ background: '#fff', borderRadius: 12, padding: '20px 24px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)', flex: 1, minWidth: 220 }}}}>
      <div style={{{{ fontSize: 13, color: '#8a8a8a', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 12 }}}}>{{label}}</div>
      <div style={{{{ display: 'flex', gap: 24, marginBottom: 10 }}}}>
        <div>
          <div style={{{{ fontSize: 12, color: CORES.REST, fontWeight: 600 }}}}>REST</div>
          <div style={{{{ fontSize: 22, fontWeight: 700, color: '#1f2937' }}}}>{{rest.toLocaleString('pt-BR', {{ maximumFractionDigits: decimals }})}}{{unit}}</div>
        </div>
        <div>
          <div style={{{{ fontSize: 12, color: CORES.GraphQL, fontWeight: 600 }}}}>GraphQL</div>
          <div style={{{{ fontSize: 22, fontWeight: 700, color: '#1f2937' }}}}>{{graphql.toLocaleString('pt-BR', {{ maximumFractionDigits: decimals }})}}{{unit}}</div>
        </div>
      </div>
      <div style={{{{ fontSize: 13, color: '#059669', fontWeight: 600, background: '#ecfdf5', display: 'inline-block', padding: '4px 10px', borderRadius: 6 }}}}>
        {{reducaoPct > 0 ? '\u2193' : '\u2191'}} {{Math.abs(reducaoPct)}}% com {{melhor}}
      </div>
    </div>
  );
}}

export default function Dashboard() {{
  const [metrica, setMetrica] = useState('tempo');

  const metricKey = metrica === 'tempo' ? 'tempo_medio' : 'tamanho_medio';
  const dadosGrafico = pivot(metricKey);
  const unidade = metrica === 'tempo' ? ' ms' : ' B';

  return (
    <div style={{{{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', background: '#f4f5f7', minHeight: '100vh', padding: 24 }}}}>
      <div style={{{{ maxWidth: 1100, margin: '0 auto' }}}}>

        <div style={{{{ marginBottom: 24 }}}}>
          <h1 style={{{{ fontSize: 26, fontWeight: 800, color: '#1f2937', margin: 0 }}}}>GraphQL vs REST \u2014 Dashboard de Resultados</h1>
          <p style={{{{ color: '#6b7280', marginTop: 6, fontSize: 14 }}}}>
            Experimento controlado \u00b7 API do GitHub \u00b7 {n_repos} reposit\u00f3rios \u00b7 {n_total_bruto} medi\u00e7\u00f5es brutas coletadas
          </p>
        </div>

        <div style={{{{ display: 'flex', gap: 16, marginBottom: 24, flexWrap: 'wrap' }}}}>
          <StatCard label="Tempo de Resposta (m\u00e9dia)" rest={{descritivas.REST.tempo.media}} graphql={{descritivas.GraphQL.tempo.media}} unit=" ms" />
          <StatCard label="Tamanho da Resposta (m\u00e9dia)" rest={{descritivas.REST.tamanho.media}} graphql={{descritivas.GraphQL.tamanho.media}} unit=" B" decimals={{0}} />
        </div>

        <div style={{{{ background: '#fff', borderRadius: 12, padding: 20, boxShadow: '0 1px 3px rgba(0,0,0,0.08)', marginBottom: 24 }}}}>
          <div style={{{{ fontSize: 13, color: '#8a8a8a', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 14 }}}}>
            Testes de Hip\u00f3tese (\u03b1 = 0,05)
          </div>
          <div style={{{{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}}}>
            {{testes.map(t => (
              <div key={{t.rq}} style={{{{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 14 }}}}>
                <div style={{{{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}}}>
                  <span style={{{{ fontWeight: 700, color: '#1f2937' }}}}>{{t.rq}} \u2014 {{t.metrica}}</span>
                  <span style={{{{ fontSize: 12, fontWeight: 700, color: t.significativo ? '#059669' : '#dc2626', background: t.significativo ? '#ecfdf5' : '#fef2f2', padding: '3px 8px', borderRadius: 6 }}}}>
                    {{t.significativo ? 'SIGNIFICATIVO' : 'N\u00c3O SIGNIFICATIVO'}}
                  </span>
                </div>
                <div style={{{{ fontSize: 13, color: '#6b7280', lineHeight: 1.6 }}}}>
                  Teste: {{t.teste}}<br/>
                  Estat\u00edstica: {{t.estatistica}} \u00b7 p-valor: {{t.p}}<br/>
                  Diferen\u00e7a mediana (REST \u2212 GraphQL): <strong>{{t.diff}}</strong>
                </div>
              </div>
            ))}}
          </div>
        </div>

        <div style={{{{ display: 'flex', gap: 8, marginBottom: 16 }}}}>
          {{['tempo', 'tamanho'].map(m => (
            <button
              key={{m}}
              onClick={{() => setMetrica(m)}}
              style={{{{
                padding: '8px 16px', borderRadius: 8, border: 'none', cursor: 'pointer',
                fontWeight: 600, fontSize: 13,
                background: metrica === m ? '#1f2937' : '#fff',
                color: metrica === m ? '#fff' : '#6b7280',
                boxShadow: '0 1px 2px rgba(0,0,0,0.06)'
              }}}}
            >
              {{m === 'tempo' ? 'Tempo de Resposta' : 'Tamanho da Resposta'}}
            </button>
          ))}}
        </div>

        <div style={{{{ background: '#fff', borderRadius: 12, padding: 20, boxShadow: '0 1px 3px rgba(0,0,0,0.08)', marginBottom: 24 }}}}>
          <div style={{{{ fontSize: 14, fontWeight: 700, color: '#1f2937', marginBottom: 16 }}}}>
            {{metrica === 'tempo' ? 'Tempo M\u00e9dio de Resposta por Reposit\u00f3rio' : 'Tamanho M\u00e9dio de Resposta por Reposit\u00f3rio'}}
          </div>
          <ResponsiveContainer width="100%" height={{360}}>
            <BarChart data={{dadosGrafico}} margin={{{{ top: 10, right: 10, left: 0, bottom: 60 }}}}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
              <XAxis dataKey="repositorio" angle={{-35}} textAnchor="end" interval={{0}} tick={{{{ fontSize: 11 }}}} />
              <YAxis tick={{{{ fontSize: 11 }}}} label={{{{ value: metrica === 'tempo' ? 'ms' : 'bytes', angle: -90, position: 'insideLeft', fontSize: 12 }}}} />
              <Tooltip formatter={{(v) => v.toLocaleString('pt-BR', {{ maximumFractionDigits: 1 }}) + unidade}} />
              <Legend />
              <Bar dataKey="REST" fill={{CORES.REST}} radius={{[4, 4, 0, 0]}} />
              <Bar dataKey="GraphQL" fill={{CORES.GraphQL}} radius={{[4, 4, 0, 0]}} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div style={{{{ fontSize: 12, color: '#9ca3af', textAlign: 'center', paddingBottom: 12 }}}}>
          LAB05 \u00b7 Laborat\u00f3rio de Experimenta\u00e7\u00e3o de Software \u00b7 PUC Minas
        </div>
      </div>
    </div>
  );
}}
"""

with open(os.path.join(BASE, "dashboard.jsx"), "w", encoding="utf-8") as f:
    f.write(dashboard_jsx)

print("dashboard.jsx atualizado com os números reais.")
print("\nPróximo passo: rode 'node scripts/gerar_relatorio.js' para gerar o .docx final.")
