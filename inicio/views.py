from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from atividades.models import Atividade
from diagnostico.models import DiagnosticoESG

# Uma dica por semana: a dica muda sozinha a cada semana do ano.
DICAS = [
    {"icone": "ci-scissors", "texto": "Reduzir o desperdício de tecido pode gerar economia e diminuir o impacto ambiental da sua produção."},
    {"icone": "ci-recycle", "texto": "Reaproveite retalhos em novas peças e acessórios, ou doe para ateliês e cooperativas da sua região."},
    {"icone": "ci-droplet", "texto": "Anote o consumo de água todo mês e defina uma meta de redução. O que é medido, melhora."},
    {"icone": "ci-shield-check", "texto": "Um canal de denúncias simples, como um e-mail ou formulário, já fortalece a governança da empresa."},
    {"icone": "ci-users", "texto": "Treinamentos curtos de segurança e ergonomia ajudam a prevenir acidentes e melhoram o clima da equipe."},
    {"icone": "ci-truck", "texto": "Pergunte aos fornecedores a origem das matérias-primas e registre as respostas em uma planilha."},
    {"icone": "ci-book-open", "texto": "Escreva um Código de Ética de uma página e compartilhe com todos os colaboradores."},
    {"icone": "ci-bulb", "texto": "Trocar lâmpadas por LED e desligar máquinas paradas são mudanças pequenas que reduzem a conta de energia."},
]

@login_required
def inicio(request):
    # Os dois diagnósticos mais recentes: o atual e o anterior (para a variação)
    recentes = list(DiagnosticoESG.objects.filter(usuario=request.user).order_by('-data_criacao')[:2])

    score = None
    variacao = None
    if recentes:
        score = recentes[0].calcular_pontuacao()
        if len(recentes) > 1:
            anterior = recentes[1].calcular_pontuacao()
            variacao = round(score['geral'] - anterior['geral'], 1)

    acoes = Atividade.objects.filter(status='andamento')
    semana = date.today().isocalendar()[1]

    return render(request, 'inicio/inicio.html', {
        'empresa': recentes[0].nome_empresa.strip() if recentes else None,
        'score': score,
        'variacao': variacao,
        'acoes': acoes[:5],
        'total_acoes': acoes.count(),
        'dica': DICAS[semana % len(DICAS)],
    })
