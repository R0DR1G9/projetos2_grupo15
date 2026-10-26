import copy

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from atividades.models import Atividade

from . import perguntas
from .forms import DiagnosticoForm
from .models import VERSAO_ATUAL, DiagnosticoESG, classificar

LIMITE_RECOMENDACOES = 10  # quantas ações aparecem na tela e entram em "adicionar todas"

NOMES_CATEGORIA = {'ambiental': 'Ambiental', 'social': 'Social', 'governanca': 'Governança'}


@login_required
def home(request):
    lista = [
        {'objeto': d, 'pontuacao': d.calcular_pontuacao()}
        for d in DiagnosticoESG.objects.filter(usuario=request.user).order_by('-data_criacao')
    ]
    return render(request, 'diagnostico/index.html', {'diagnosticos': lista})


def _pilares_do_formulario(respostas):
    """Cópia do banco de perguntas com a resposta marcada, para repopular o formulário."""
    pilares = copy.deepcopy(perguntas.PILARES)
    for pilar in pilares:
        for sub in pilar['subtemas']:
            for p in sub['perguntas']:
                valor = respostas.get(p['id'], 'ausente')
                p['valor'] = 'na' if valor is None else (None if valor == 'ausente' else valor)
                p['aplica_texto'] = ' '.join(p['aplica'])
                p['opcoes'] = [(i, perguntas.NOMES_NIVEL[i], texto) for i, texto in enumerate(p['niveis'])]
    return pilares


@login_required
def novo_diagnostico(request):
    erro_respostas = False
    respostas = {}
    if request.method == 'POST':
        form = DiagnosticoForm(request.POST)
        tipo = request.POST.get('tipo_operacao', '')
        respostas, faltando = perguntas.ler_respostas(request.POST, tipo)
        erro_respostas = bool(faltando)
        if form.is_valid() and not faltando:
            diagnostico = form.save(commit=False)
            diagnostico.respostas = respostas
            diagnostico.versao_questionario = VERSAO_ATUAL
            diagnostico.usuario = request.user
            diagnostico.save()
            return redirect('resultado_diagnostico', pk=diagnostico.pk)
    else:
        form = DiagnosticoForm(initial={'nome_empresa': request.user.first_name})

    return render(request, 'diagnostico/form.html', {
        'form': form,
        'pilares': _pilares_do_formulario(respostas),
        'escala': perguntas.ESCALA,
        'erro_respostas': erro_respostas,
        'total_perguntas': len(perguntas.PERGUNTAS),
    })


@login_required
def resultado(request, pk):
    diagnostico = get_object_or_404(DiagnosticoESG, pk=pk, usuario=request.user)
    pontuacao = diagnostico.calcular_pontuacao()
    contexto = {'diagnostico': diagnostico, 'pontuacao': pontuacao}

    if not diagnostico.formato_antigo:
        notas = perguntas.pontuar(diagnostico.respostas)
        pilares = []
        for pilar in perguntas.PILARES:
            nota = notas[pilar['chave']]
            pilares.append({
                'chave': pilar['chave'], 'nome': pilar['nome'], 'sigla': pilar['sigla'],
                'pct': nota['pct'], 'medalha': classificar(nota['pct']), 'subtemas': nota['subtemas'],
            })
        titulos_no_plano = set(Atividade.objects.values_list('titulo', flat=True))
        recomendacoes = perguntas.recomendacoes(diagnostico.respostas, LIMITE_RECOMENDACOES)
        for r in recomendacoes:
            r['categoria_nome'] = NOMES_CATEGORIA[r['categoria']]
            r['no_plano'] = r['acao'] in titulos_no_plano
        contexto.update({
            'pilares': pilares,
            'recomendacoes': recomendacoes,
            'pendentes': sum(1 for r in recomendacoes if not r['no_plano']),
            'pontos_fortes': perguntas.pontos_fortes(diagnostico.respostas),
            'nao_se_aplica': sum(1 for v in diagnostico.respostas.values() if v is None),
        })
    return render(request, 'diagnostico/resultado.html', contexto)


def metodologia(request):
    fontes = perguntas.FONTES
    linhas = []
    for pilar in perguntas.PILARES:
        for sub in pilar['subtemas']:
            for p in sub['perguntas']:
                linhas.append({
                    'pilar': pilar['nome'], 'subtema': sub['nome'], 'texto': p['texto'], 'peso': p['peso'],
                    'fontes': [fontes[f] for f in p['fontes']],
                    'aplica': [dict(perguntas.TIPOS_OPERACAO)[t] for t in p['aplica']] if len(p['aplica']) < 4 else None,
                })
    return render(request, 'diagnostico/metodologia.html', {
        'escala': perguntas.ESCALA, 'fontes': fontes.values(), 'linhas': linhas,
        'total_perguntas': len(perguntas.PERGUNTAS),
    })


@login_required
@require_POST
def adicionar_ao_plano(request, pk):
    """Cria atividades em 'Aguardando início' a partir das recomendações do diagnóstico."""
    diagnostico = get_object_or_404(DiagnosticoESG, pk=pk, usuario=request.user)
    destino = redirect('resultado_diagnostico', pk=pk)
    destino['Location'] += '#recomendacoes'
    if diagnostico.formato_antigo:
        return destino

    todas = perguntas.recomendacoes(diagnostico.respostas, LIMITE_RECOMENDACOES)
    if request.POST.get('todas'):
        escolhidas = todas
    else:
        escolhidas = [r for r in todas if r['id'] == request.POST.get('pergunta')]

    criadas = 0
    for r in escolhidas:
        _, criada = Atividade.objects.get_or_create(
            titulo=r['acao'],
            defaults={
                'categoria': r['categoria'], 'status': 'aguardando',
                'descricao': f"Pronto quando: {r['pronto']}. Prazo sugerido: {r['prazo']} dias.",
            },
        )
        criadas += criada

    if criadas:
        messages.success(request, f'{criadas} ação(ões) adicionada(s) ao Plano de Ação, em "Aguardando início".')
    else:
        messages.info(request, 'Essas ações já estão no seu Plano de Ação.')
    return destino


@login_required
@require_POST
def deletar_diagnostico(request, pk):
    diagnostico = get_object_or_404(DiagnosticoESG, pk=pk, usuario=request.user)
    diagnostico.delete()
    return JsonResponse({'success': True})
