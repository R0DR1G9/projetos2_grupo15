from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from diagnostico import pdf
from diagnostico.models import DiagnosticoESG
from django.contrib.auth.decorators import login_required

def _dados_evolucao(usuario):
    diagnosticos = list(DiagnosticoESG.objects.filter(usuario=usuario).order_by('data_criacao'))
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
    resultado = _dados_evolucao(request.user)
    if resultado is None:
        messages.error(request, 'É preciso ao menos dois diagnósticos para exportar a evolução.', extra_tags='danger')
        return redirect('evolucao')
    dados, _ = resultado
    conteudo = pdf.gerar_pdf_evolucao(request.user, dados, dados['geral'][-1], round(dados['geral'][-1] - dados['geral'][-2], 1))
    resposta = HttpResponse(conteudo, content_type='application/pdf')
    resposta['Content-Disposition'] = 'attachment; filename="evolucao-esg.pdf"'
    return resposta
