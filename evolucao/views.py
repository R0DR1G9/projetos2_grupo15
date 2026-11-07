import datetime

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from diagnostico import pdf
from diagnostico.models import DiagnosticoESG
from django.contrib.auth.decorators import login_required

def _ler_data(texto):
    try:
        return datetime.date.fromisoformat(texto) if texto else None
    except ValueError:
        return False


def _dados_evolucao(usuario, inicio=None, fim=None):
    consulta = DiagnosticoESG.objects.filter(usuario=usuario)
    if inicio:
        consulta = consulta.filter(data_criacao__date__gte=inicio)
    if fim:
        consulta = consulta.filter(data_criacao__date__lte=fim)
    diagnosticos = list(consulta.order_by('data_criacao'))
    if len(diagnosticos) < 2:
        return None
    dados = {'rotulos': [], 'datas': [], 'empresas': [],
             'geral': [], 'ambiental': [], 'social': [], 'governanca': []}
    for i, d in enumerate(diagnosticos, start=1):
        p = d.calcular_pontuacao()
        dados['rotulos'].append(f"Diagnóstico {i}")
        dados['datas'].append(f"{timezone.localtime(d.data_criacao):%d/%m/%Y %H:%M}")
        dados['empresas'].append(d.nome_empresa)
        dados['geral'].append(p['geral'])
        dados['ambiental'].append(p['ambiental'])
        dados['social'].append(p['social'])
        dados['governanca'].append(p['governanca'])
    return dados, len(diagnosticos)


@login_required
def evolucao(request):
    resultado = _dados_evolucao(request.user)
    if resultado is None:
        return render(request, 'evolucao/evolucao.html', {'dados_suficientes': False})
    dados, total = resultado
    nota_atual = dados['geral'][-1]
    variacao = round(nota_atual - dados['geral'][-2], 1)
    return render(request, 'evolucao/evolucao.html', {
        'dados_suficientes': True,
        'dados': dados,
        'nota_atual': nota_atual,
        'variacao': variacao,
        'total': total,
    })


@login_required
def evolucao_pdf(request):
    inicio = _ler_data(request.GET.get('de'))
    fim = _ler_data(request.GET.get('ate'))
    if inicio is False or fim is False:
        messages.error(request, 'Use datas válidas no filtro de período.', extra_tags='danger')
        return redirect('evolucao')
    if inicio and fim and inicio > fim:
        messages.error(request, 'A data inicial não pode ser depois da data final.', extra_tags='danger')
        return redirect('evolucao')
    resultado = _dados_evolucao(request.user, inicio, fim)
    if resultado is None:
        if inicio or fim:
            texto = 'Há menos de dois diagnósticos nesse período. Escolha um período maior.'
        else:
            texto = 'É preciso ao menos dois diagnósticos para exportar a evolução.'
        messages.error(request, texto, extra_tags='danger')
        return redirect('evolucao')
    dados, _ = resultado
    periodo = None
    if inicio or fim:
        de = f'{inicio:%d/%m/%Y}' if inicio else 'o primeiro diagnóstico'
        ate = f'{fim:%d/%m/%Y}' if fim else 'hoje'
        periodo = f'Período: de {de} até {ate}'
    conteudo = pdf.gerar_pdf_evolucao(request.user, dados, dados['geral'][-1], round(dados['geral'][-1] - dados['geral'][-2], 1), periodo)
    resposta = HttpResponse(conteudo, content_type='application/pdf')
    resposta['Content-Disposition'] = 'attachment; filename="evolucao-esg.pdf"'
    return resposta
