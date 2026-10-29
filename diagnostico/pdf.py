from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

VINHO = colors.HexColor('#673a40')
OURO = colors.HexColor('#d6c67b')
CREME = colors.HexColor('#fae4b2')
BEGE = colors.HexColor('#fdf1d8')
TEXTO = colors.HexColor('#2f2123')
SUAVE = colors.HexColor('#7a6468')

_base = getSampleStyleSheet()
TITULO = ParagraphStyle('titulo', parent=_base['Title'], fontName='Helvetica-Bold', fontSize=20, textColor=VINHO, alignment=0, spaceAfter=2)
SUB = ParagraphStyle('sub', parent=_base['Normal'], fontSize=9.5, textColor=SUAVE, leading=13)
H2 = ParagraphStyle('h2', parent=_base['Heading2'], fontName='Helvetica-Bold', fontSize=13, textColor=VINHO, spaceBefore=14, spaceAfter=6)
CORPO = ParagraphStyle('corpo', parent=_base['Normal'], fontSize=9.5, textColor=TEXTO, leading=13)
PEQUENO = ParagraphStyle('pequeno', parent=CORPO, fontSize=8.5, textColor=SUAVE, leading=11)
NEGRITO = ParagraphStyle('negrito', parent=CORPO, fontName='Helvetica-Bold')
GRANDE = ParagraphStyle('grande', parent=CORPO, fontName='Helvetica-Bold', fontSize=22, leading=28, textColor=VINHO)
MEDIO = ParagraphStyle('medio', parent=GRANDE, fontSize=17, leading=28)
CENTRO = ParagraphStyle('centro', parent=CORPO, alignment=TA_CENTER)


def _esc(texto):
    return str(texto).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(SUAVE)
    canvas.drawString(2 * cm, 1.2 * cm, 'Plataforma ESG - relatório gerado automaticamente')
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f'Página {doc.page}')
    canvas.restoreState()


def _cabecalho(titulo, linhas):
    itens = [Paragraph(_esc(titulo), TITULO)]
    itens += [Paragraph(_esc(l), SUB) for l in linhas if l]
    faixa = Table([['']], colWidths=[17 * cm], rowHeights=[3])
    faixa.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), OURO)]))
    itens += [Spacer(1, 6), faixa, Spacer(1, 6)]
    return itens


def _tabela(dados, larguras, cabecalho=True):
    t = Table(dados, colWidths=larguras, repeatRows=1 if cabecalho else 0)
    estilo = [
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), TEXTO),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1 if cabecalho else 0), (-1, -1), [colors.white, BEGE]),
        ('LINEBELOW', (0, 0), (-1, -1), 0.3, CREME),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]
    if cabecalho:
        estilo += [('BACKGROUND', (0, 0), (-1, 0), VINHO), ('TEXTCOLOR', (0, 0), (-1, 0), CREME), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')]
    t.setStyle(TableStyle(estilo))
    return t


def _fmt(valor):
    return f'{valor:.1f}'.replace('.', ',').replace(',0', '') + '%'


def _empresa_linha(usuario):
    empresa = getattr(usuario, 'empresa', None)
    return f'CNPJ: {empresa.cnpj_formatado}' if empresa else ''


def _montar(elementos):
    saida = BytesIO()
    doc = SimpleDocTemplate(saida, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2 * cm, title='Relatório ESG', author='Plataforma ESG')
    doc.build(elementos, onFirstPage=_rodape, onLaterPages=_rodape)
    return saida.getvalue()


def gerar_pdf_diagnostico(diagnostico, usuario, pontuacao, pilares, recomendacoes, pontos_fortes):
    data = diagnostico.data_criacao
    from django.utils import timezone
    data = timezone.localtime(data)
    el = _cabecalho('Resultado do diagnóstico ESG', [
        diagnostico.nome_empresa,
        _empresa_linha(usuario),
        f'Realizado em {data:%d/%m/%Y} às {data:%H:%M}',
    ])

    medalha = pontuacao['medalha_geral']
    resumo = [
        [Paragraph('Nota ESG geral', PEQUENO), Paragraph('Seu nível', PEQUENO), Paragraph('Próximo nível', PEQUENO)],
        [Paragraph(_fmt(pontuacao['geral']), GRANDE),
         Paragraph(medalha['nome'], MEDIO),
         Paragraph(
             f'Faltam {_fmt(pontuacao["proximo_nivel"]["faltam"])[:-1]} pontos para {pontuacao["proximo_nivel"]["nome"]}'
             if pontuacao.get('proximo_nivel') else 'Nível máximo alcançado', CORPO)],
    ]
    t = Table(resumo, colWidths=[5 * cm, 5 * cm, 7 * cm])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), BEGE), ('BOX', (0, 0), (-1, -1), 0.6, OURO), ('LEFTPADDING', (0, 0), (-1, -1), 10), ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
    el.append(t)

    if pilares:
        el.append(Paragraph('Nota por pilar', H2))
        linhas = [['Pilar', 'Nota', 'Nível']]
        for p in pilares:
            linhas.append([f'{p["nome"]} ({p["sigla"]})', _fmt(p['pct']), p['medalha']['nome']])
        el.append(_tabela(linhas, [9 * cm, 4 * cm, 4 * cm]))

        el.append(Paragraph('Nota por subtema', H2))
        linhas = [['Pilar', 'Subtema', 'Nota']]
        for p in pilares:
            for s in p['subtemas']:
                linhas.append([p['nome'], s['nome'], _fmt(s['pct'])])
        el.append(_tabela(linhas, [4.5 * cm, 9.5 * cm, 3 * cm]))

        el.append(Paragraph('O que fazer primeiro', H2))
        if recomendacoes:
            for i, r in enumerate(recomendacoes, start=1):
                el.append(Paragraph(f'<b>{i}. {_esc(r["acao"])}</b>', CORPO))
                el.append(Paragraph(f'{_esc(r["categoria_nome"])} - prioridade {_esc(r["prioridade"]).lower()} - prazo de {r["prazo"]} dias', PEQUENO))
                el.append(Paragraph(f'<b>Pronto quando:</b> {_esc(r["pronto"])}.', PEQUENO))
                el.append(Spacer(1, 6))
        else:
            el.append(Paragraph('Todas as áreas respondidas estão em nível Gerenciado ou acima.', CORPO))

        el.append(Paragraph('Pontos fortes', H2))
        if pontos_fortes:
            for f in pontos_fortes:
                el.append(Paragraph(f'<b>{_esc(f["subtema"])} - {_esc(f["nivel_nome"])}</b>', CORPO))
                el.append(Paragraph(_esc(f['descricao']), PEQUENO))
                el.append(Spacer(1, 4))
        else:
            el.append(Paragraph('Ainda não há áreas em nível Gerenciado ou Integrado.', CORPO))
    else:
        el.append(Spacer(1, 8))
        el.append(Paragraph('Este diagnóstico foi feito no formato antigo (sim ou não), por isso não tem análise detalhada.', CORPO))

    dados = []
    if diagnostico.numero_funcionarios is not None:
        dados.append(['Funcionários', str(diagnostico.numero_funcionarios)])
    if diagnostico.kg_sobras_geradas is not None:
        pct = diagnostico.pct_residuos_reaproveitados
        dados.append(['Sobras de tecido reaproveitadas', f'{diagnostico.kg_sobras_reaproveitadas or 0} de {diagnostico.kg_sobras_geradas} kg' + (f' ({pct}%)' if pct is not None else '')])
    if diagnostico.pessoas_lideranca is not None:
        pct = diagnostico.pct_mulheres_lideranca
        dados.append(['Mulheres na liderança', f'{diagnostico.mulheres_lideranca or 0} de {diagnostico.pessoas_lideranca}' + (f' ({pct}%)' if pct is not None else '')])
    if diagnostico.horas_treinamento_ano is not None:
        dados.append(['Treinamento por pessoa ao ano', f'{diagnostico.horas_treinamento_ano} h'])
    if dados:
        el.append(Paragraph('Seus números', H2))
        el.append(_tabela(dados, [9 * cm, 8 * cm], cabecalho=False))

    el.append(Spacer(1, 12))
    el.append(Paragraph('Nota calculada por média ponderada dos níveis de maturidade (0 a 4). Metodologia e fontes disponíveis na plataforma.', PEQUENO))
    return _montar(el)


def gerar_pdf_evolucao(usuario, dados, nota_atual, variacao):
    from reportlab.graphics.charts.lineplots import LinePlot
    from reportlab.graphics.shapes import Drawing

    el = _cabecalho('Evolução ESG', [usuario.first_name or usuario.get_username(), _empresa_linha(usuario)])
    sinal = f'+{variacao}' if variacao > 0 else str(variacao)
    el.append(Paragraph(f'Nota geral atual: <b>{_fmt(nota_atual)}</b> - variação em relação ao diagnóstico anterior: <b>{sinal} pontos</b>', CORPO))

    n = len(dados['geral'])
    desenho = Drawing(17 * cm, 7 * cm)
    grafico = LinePlot()
    grafico.x, grafico.y, grafico.width, grafico.height = 35, 25, 17 * cm - 60, 7 * cm - 45
    series = [('geral', VINHO), ('ambiental', colors.HexColor('#3e462f')), ('social', colors.HexColor('#7d2028')), ('governanca', colors.HexColor('#5fa8c2'))]
    grafico.data = [[(i + 1, v) for i, v in enumerate(dados[chave])] for chave, _ in series]
    for i, (_, cor) in enumerate(series):
        grafico.lines[i].strokeColor = cor
        grafico.lines[i].strokeWidth = 2 if i == 0 else 1.2
    grafico.yValueAxis.valueMin, grafico.yValueAxis.valueMax, grafico.yValueAxis.valueStep = 0, 100, 20
    grafico.xValueAxis.valueMin, grafico.xValueAxis.valueMax, grafico.xValueAxis.valueStep = 1, max(n, 2), 1
    grafico.xValueAxis.labelTextFormat = '%d'
    grafico.xValueAxis.labels.fontSize = grafico.yValueAxis.labels.fontSize = 8
    desenho.add(grafico)
    el.append(Spacer(1, 8))
    el.append(desenho)
    el.append(Paragraph('Linhas: geral (vinho), ambiental (oliva), social (vinho escuro), governança (azul). Eixo horizontal: número do diagnóstico.', PEQUENO))

    el.append(Paragraph('Histórico de diagnósticos', H2))
    linhas = [['#', 'Data', 'Geral', 'Ambiental', 'Social', 'Governança']]
    for i in range(n):
        linhas.append([str(i + 1), dados['datas'][i], _fmt(dados['geral'][i]), _fmt(dados['ambiental'][i]), _fmt(dados['social'][i]), _fmt(dados['governanca'][i])])
    el.append(_tabela(linhas, [1 * cm, 4.5 * cm, 2.5 * cm, 3 * cm, 3 * cm, 3 * cm]))
    return _montar(el)
