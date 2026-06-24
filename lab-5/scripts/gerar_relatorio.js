const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        ImageRun, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
        WidthType, ShadingType, PageNumber, Footer, Header } = require('docx');
const fs = require('fs');

const GRAF = '/home/claude/lab05_real/scripts/../graficos';

function imgBuf(path) { return fs.readFileSync(path); }

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

function headerCell(text, width) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: "2E5C8A", type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF" })] })]
  });
}

function cell(text, width) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({ children: [new TextRun(text)] })]
  });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: "1F3864" },
        paragraph: { spacing: { before: 320, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "2E5C8A" },
        paragraph: { spacing: { before: 260, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: "2E5C8A" },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022",
        alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.",
        alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    properties: {
      page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } }
    },
    headers: {
      default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: "LAB05 — GraphQL vs REST", size: 18, color: "888888" })]
      })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Página ", size: 18, color: "888888" }),
                    new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "888888" })]
      })] })
    },
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 80 },
        children: [new TextRun({ text: "GraphQL vs REST", bold: true, size: 44, color: "1F3864" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 40 },
        children: [new TextRun({ text: "Um Experimento Controlado", size: 28, color: "2E5C8A" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 400 },
        children: [new TextRun({ text: "Laboratório de Experimentação de Software — PUC Minas", size: 20, italics: true, color: "666666" })]
      }),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Introdução")] }),
      new Paragraph({
        spacing: { after: 160 },
        children: [new TextRun(
          "GraphQL é uma linguagem de consulta para APIs Web, proposta pelo Facebook, baseada em " +
          "grafos e schemas definidos pelo servidor, permitindo que o cliente especifique exatamente " +
          "quais campos deseja obter em uma única requisição. Em contraste, APIs REST organizam-se em " +
          "torno de endpoints fixos, frequentemente retornando estruturas de dados predefinidas que podem " +
          "conter mais informação do que o cliente necessita (overfetching) ou exigir múltiplas chamadas " +
          "para compor a informação desejada (underfetching)."
        )]
      }),
      new Paragraph({
        spacing: { after: 160 },
        children: [new TextRun(
          "Este relatório descreve um experimento controlado, com desenho pareado (within-subject), " +
          "comparando o desempenho de consultas equivalentes realizadas via API REST e API GraphQL do " +
          "GitHub, com o objetivo de responder quantitativamente às seguintes perguntas de pesquisa:"
        )]
      }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 80 },
        children: [new TextRun({ text: "RQ1: ", bold: true }), new TextRun("Respostas às consultas GraphQL são mais rápidas que respostas às consultas REST?")] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 200 },
        children: [new TextRun({ text: "RQ2: ", bold: true }), new TextRun("Respostas às consultas GraphQL têm tamanho menor que respostas às consultas REST?")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.1 Hipóteses")] }),
      new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: "Para RQ1 (tempo de resposta):", bold: true })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("H0₁: não há diferença significativa no tempo de resposta entre GraphQL e REST.")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 160 }, children: [new TextRun("H1₁: existe diferença significativa no tempo de resposta entre GraphQL e REST.")] }),
      new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: "Para RQ2 (tamanho de resposta):", bold: true })] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("H0₂: não há diferença significativa no tamanho de resposta entre GraphQL e REST.")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 160 }, children: [new TextRun("H1₂: existe diferença significativa no tamanho de resposta entre GraphQL e REST.")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Metodologia")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 Variáveis")] }),
      new Paragraph({ children: [new TextRun({ text: "Variável independente: ", bold: true }), new TextRun("tipo de API utilizada (REST ou GraphQL), categórica com 2 níveis.")] }),
      new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "Variáveis dependentes: ", bold: true }), new TextRun("(i) tempo de resposta, em milissegundos; (ii) tamanho da resposta, em bytes.")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 Tratamentos e Objetos Experimentais")] }),
      new Paragraph({ spacing: { after: 160 }, children: [new TextRun(
        "Foram definidos dois tratamentos: (T1) consulta via API REST do GitHub e (T2) consulta " +
        "equivalente via API GraphQL do GitHub. Os objetos experimentais consistem em 10 repositórios " +
        "públicos (mesmo conjunto utilizado nos dois tratamentos), consultados para os mesmos dados: nome, " +
        "descrição, número de estrelas, número de forks, linguagem principal e as 5 issues abertas mais recentes."
      )]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.3 Tipo de Projeto Experimental")] }),
      new Paragraph({ spacing: { after: 160 }, children: [new TextRun(
        "Foi adotado um desenho pareado (within-subject / paired design): cada repositório foi consultado " +
        "por ambos os tratamentos, controlando a variação entre objetos experimentais e aumentando o poder " +
        "estatístico do teste de hipótese, já que cada par de observações compartilha o mesmo objeto."
      )]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.4 Quantidade de Medições")] }),
      new Paragraph({ spacing: { after: 160 }, children: [new TextRun(
        "Foram coletadas 600 medições brutas, das quais 276 (tratamento REST) e 295 " +
        "(tratamento GraphQL) permaneceram após validação e remoção de outliers via IQR. A ordem de " +
        "execução dos tratamentos e dos repositórios foi aleatorizada a cada repetição, de modo a mitigar " +
        "efeitos de hora do dia, cache e variação de rede."
      )]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.5 Ambiente e Reprodutibilidade")] }),
      new Paragraph({ spacing: { after: 80 }, children: [new TextRun(
        "O experimento foi implementado em Python 3.12, utilizando a biblioteca requests para realizar " +
        "as chamadas HTTP. As medições de tempo foram feitas com time.perf_counter(), capturando o " +
        "intervalo entre o início da requisição e o recebimento completo da resposta. O tamanho da " +
        "resposta foi obtido a partir do corpo (body) retornado pela API, em bytes."
      )]}),
      new Paragraph({ spacing: { after: 80 }, children: [new TextRun(
        "Para a API REST, como não existe um único endpoint que combine dados do repositório e issues, " +
        "a medição de cada trial soma o tempo e o tamanho de duas chamadas: GET /repos/{owner}/{repo} e " +
        "GET /repos/{owner}/{repo}/issues. Para a API GraphQL, uma única consulta (query) equivalente " +
        "retorna o mesmo conjunto de dados em uma única chamada POST."
      )]}),
      new Paragraph({ spacing: { after: 160 }, children: [new TextRun(
        "Os scripts de coleta (coletar_dados.py), análise estatística (analisar_dados.py) e geração de " +
        "gráficos (gerar_graficos.py) estão disponíveis no pacote de arquivos deste laboratório, permitindo " +
        "a reprodução integral do experimento mediante um GitHub Personal Access Token válido."
      )]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.6 Análise Estatística")] }),
      new Paragraph({ spacing: { after: 160 }, children: [new TextRun(
        "Após a coleta, os dados passaram por validação (remoção de medições com falha) e remoção de " +
        "outliers via método IQR (intervalo interquartil) por tratamento. Em seguida, foi aplicado o " +
        "teste de Shapiro-Wilk para verificar normalidade das distribuições. Como ao menos um dos grupos não apresentou distribuição compatível com normalidade (p ≤ 0,05 no teste de Shapiro-Wilk), foi utilizado o teste de Wilcoxon pareado (não-paramétrico) para comparar as métricas entre os tratamentos, ao nível de significância de 5% (α = 0,05)."
      )]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.7 Ameaças à Validade")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Validade interna: ", bold: true }), new TextRun("variações de latência de rede e cache durante a coleta foram mitigadas por meio de aleatorização da ordem de execução e múltiplas repetições.")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Validade externa: ", bold: true }), new TextRun("os resultados refletem o comportamento específico da API do GitHub, podendo não generalizar diretamente para outras APIs ou domínios.")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Validade de construto: ", bold: true }), new TextRun("o tempo medido no cliente inclui latência de rede, não isolando apenas o tempo de processamento no servidor.")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 160 }, children: [new TextRun({ text: "Validade de conclusão: ", bold: true }), new TextRun("o tamanho amostral e os testes estatísticos apropriados reduzem o risco de conclusões espúrias.")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. Resultados")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 Estatística Descritiva")] }),
      new Paragraph({ spacing: { after: 160 }, children: [new TextRun(
        "A Tabela 1 apresenta as estatísticas descritivas das medições válidas (após remoção de " +
        "outliers) para cada tratamento e métrica."
      )]}),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2200, 1700, 1500, 1700, 1130, 1130],
        rows: [
          new TableRow({ children: [
            headerCell("Métrica", 2200), headerCell("Tratamento", 1700), headerCell("Média", 1500),
            headerCell("Mediana", 1700), headerCell("Desvio Padrão", 1130), headerCell("n", 1130)
          ]}),
          new TableRow({ children: [
            cell("Tempo de Resposta (ms)", 2200), cell("REST", 1700), cell("1.382,98", 1500),
            cell("1.365,72", 1700), cell("159,50", 1130), cell("276", 1130)
          ]}),
          new TableRow({ children: [
            cell("Tempo de Resposta (ms)", 2200), cell("GraphQL", 1700), cell("636,99", 1500),
            cell("634,80", 1700), cell("80,21", 1130), cell("295", 1130)
          ]}),
          new TableRow({ children: [
            cell("Tamanho da Resposta (bytes)", 2200), cell("REST", 1700), cell("29.371", 1500),
            cell("25.854", 1700), cell("12.395", 1130), cell("276", 1130)
          ]}),
          new TableRow({ children: [
            cell("Tamanho da Resposta (bytes)", 2200), cell("GraphQL", 1700), cell("765", 1500),
            cell("925", 1700), cell("301", 1130), cell("295", 1130)
          ]}),
        ]
      }),
      new Paragraph({ spacing: { before: 80, after: 240 }, children: [new TextRun({ text: "Tabela 1. ", italics: true, bold: true }), new TextRun({ text: "Estatísticas descritivas por tratamento e métrica.", italics: true, size: 20 })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 RQ1 — Tempo de Resposta")] }),
      new Paragraph({ spacing: { after: 160 }, children: [new TextRun(
        "O teste de Wilcoxon pareado (não-paramétrico) indicou diferença estatisticamente significativa entre os " +
        "tratamentos (estatística = 0,00; p-valor < 0,001). A diferença mediana observada foi de aproximadamente " +
        "724,30 ms, com GraphQL apresentando tempos de resposta menores. " +
        "Dessa forma, H0₁ é rejeitada em favor de H1₁."
      )]}),
      new Paragraph({
        children: [new ImageRun({ data: imgBuf(`${GRAF}/boxplot_tempo.png`), transformation: { width: 500, height: 357 }, type: "png" })],
        alignment: AlignmentType.CENTER
      }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 80, after: 240 }, children: [new TextRun({ text: "Figura 1. Distribuição do tempo de resposta por tratamento.", italics: true, size: 20 })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.3 RQ2 — Tamanho da Resposta")] }),
      new Paragraph({ spacing: { after: 160 }, children: [new TextRun(
        "O teste de Wilcoxon pareado (não-paramétrico) indicou diferença estatisticamente significativa entre os " +
        "tratamentos (estatística = 0,00; p-valor < 0,001). A diferença mediana foi de aproximadamente " +
        "25.645 bytes, com as respostas GraphQL sendo menores. " +
        "Dessa forma, H0₂ é rejeitada em favor de H1₂."
      )]}),
      new Paragraph({
        children: [new ImageRun({ data: imgBuf(`${GRAF}/boxplot_tamanho.png`), transformation: { width: 500, height: 357 }, type: "png" })],
        alignment: AlignmentType.CENTER
      }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 80, after: 240 }, children: [new TextRun({ text: "Figura 2. Distribuição do tamanho da resposta por tratamento.", italics: true, size: 20 })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.4 Comparação por Repositório")] }),
      new Paragraph({
        children: [new ImageRun({ data: imgBuf(`${GRAF}/barras_media_por_repositorio_tamanho.png`), transformation: { width: 580, height: 348 }, type: "png" })],
        alignment: AlignmentType.CENTER
      }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 80, after: 240 }, children: [new TextRun({ text: "Figura 3. Tamanho médio da resposta por repositório e tratamento.", italics: true, size: 20 })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Discussão")] }),
      new Paragraph({ spacing: { after: 160 }, children: [new TextRun(
        "Os resultados deste experimento controlado fornecem evidência estatística de que, " +
        "no contexto da API do GitHub e para o conjunto de consultas avaliado, GraphQL apresenta respostas " +
        "mais rápidas e GraphQL apresenta respostas menores que a outra abordagem, respondendo a " +
        "RQ1 (sim) e RQ2 (sim)."
      )]}),
      new Paragraph({ spacing: { after: 160 }, children: [new TextRun(
        "A diferença no tamanho da resposta é consistente com a principal vantagem teórica do GraphQL: a " +
        "eliminação de overfetching, já que o cliente especifica exatamente os campos desejados, ao invés " +
        "de receber a estrutura completa predefinida pelo endpoint REST. A diferença no tempo de resposta, " +
        "por sua vez, pode ser parcialmente explicada pela necessidade de duas chamadas HTTP separadas no " +
        "tratamento REST (uma para dados do repositório e outra para issues), enquanto o GraphQL resolveu a " +
        "mesma necessidade em uma única requisição."
      )]}),
      new Paragraph({ spacing: { after: 160 }, children: [new TextRun(
        "É importante notar que essa vantagem pode não se generalizar para todos os cenários: em consultas " +
        "mais simples, que já mapeiam para um único endpoint REST, a diferença de tempo poderia ser menor " +
        "ou mesmo inexistente, já que o servidor GraphQL incorre em overhead adicional de resolução de " +
        "schema. O ganho mais robusto e generalizável observado neste experimento é o de tamanho de " +
        "payload, diretamente relacionado à quantidade de dados transferidos pela rede."
      )]}),
      new Paragraph({ spacing: { after: 160 }, children: [new TextRun(
        "Como trabalhos futuros, seria relevante repetir o experimento variando a complexidade das " +
        "consultas (campos aninhados, profundidade do grafo) e comparando diferentes provedores de API, " +
        "de modo a avaliar a robustez externa dessas conclusões."
      )]}),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync('/home/claude/lab05_real/scripts/../relatorio/Relatorio_Final_LAB05.docx', buffer);
  console.log('Relatório gerado com sucesso com os dados reais.');
});
