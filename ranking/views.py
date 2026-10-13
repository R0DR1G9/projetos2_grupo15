from django.shortcuts import render
from diagnostico.models import DiagnosticoESG

PILARES = [
    ('geral', 'Geral'),
    ('ambiental', 'Ambiental'),
    ('social', 'Social'),
    ('governanca', 'Governança'),
]


def ranking(request):
    pilar = request.GET.get('pilar', 'geral')
    if pilar not in dict(PILARES):
        pilar = 'geral'

    # Fica só o diagnóstico mais recente de cada empresa
    ultimos = {}
    for d in DiagnosticoESG.objects.order_by('data_criacao'):
        ultimos[d.nome_empresa.strip().lower()] = d

    linhas = []
    for d in ultimos.values():
        p = d.calcular_pontuacao()
        linhas.append({
            'empresa': d.nome_empresa.strip(),
            'p': p,
            'nota': p[pilar],
            'medalha': p['medalha_' + pilar],
            'data': d.data_criacao,
        })

    linhas.sort(key=lambda l: (-l['nota'], l['empresa'].lower()))

    # Empates dividem a mesma posição
    pos, anterior = 0, None
    for i, l in enumerate(linhas, start=1):
        if l['nota'] != anterior:
            pos, anterior = i, l['nota']
        l['posicao'] = pos

    return render(request, 'ranking/ranking.html', {
        'linhas': linhas,
        'top3': linhas[:3],
        'pilares': PILARES,
        'pilar': pilar,
    })