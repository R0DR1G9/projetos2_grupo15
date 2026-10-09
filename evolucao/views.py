from django.shortcuts import render
from diagnostico.models import DiagnosticoESG


def evolucao(request):
    diagnosticos = list(DiagnosticoESG.objects.order_by('data_criacao'))

    if len(diagnosticos) < 2:
        return render(request, 'evolucao/evolucao.html', {'dados_suficientes': False})

    dados = {'rotulos': [], 'datas': [], 'empresas': [],
             'geral': [], 'ambiental': [], 'social': [], 'governanca': []}
    for i, d in enumerate(diagnosticos, start=1):
        p = d.calcular_pontuacao()
        dados['rotulos'].append(f"Diagnóstico {i}")
        dados['datas'].append(f"{d.data_criacao:%d/%m/%Y %H:%M}")
        dados['empresas'].append(d.nome_empresa)
        dados['geral'].append(p['geral'])
        dados['ambiental'].append(p['ambiental'])
        dados['social'].append(p['social'])
        dados['governanca'].append(p['governanca'])

    nota_atual = dados['geral'][-1]
    variacao = round(nota_atual - dados['geral'][-2], 1)

    return render(request, 'evolucao/evolucao.html', {
        'dados_suficientes': True,
        'dados': dados,
        'nota_atual': nota_atual,
        'variacao': variacao,
        'total': len(diagnosticos),
    })