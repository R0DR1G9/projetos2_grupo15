from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import DiagnosticoForm
from .models import DiagnosticoESG


@login_required
def home(request):
    diagnosticos = DiagnosticoESG.objects.filter(usuario=request.user).order_by('-data_criacao')
    form = DiagnosticoForm(initial={'nome_empresa': request.user.first_name})

    lista_com_resultados = []
    for d in diagnosticos:
        lista_com_resultados.append({
            'objeto': d,
            'pontuacao': d.calcular_pontuacao()
        })

    return render(request, 'diagnostico/index.html', {
        'diagnosticos': lista_com_resultados,
        'form': form
    })


@login_required
@require_POST
def salvar_diagnostico(request):
    form = DiagnosticoForm(request.POST)
    if form.is_valid():
        diagnostico = form.save(commit=False)
        diagnostico.usuario = request.user
        diagnostico.save()
        resultados = diagnostico.calcular_pontuacao()
        return JsonResponse({
            'success': True,
            'nome_empresa': diagnostico.nome_empresa,
            'resultados': resultados
        })
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
@require_POST
def deletar_diagnostico(request, pk):
    diagnostico = get_object_or_404(DiagnosticoESG, pk=pk, usuario=request.user)
    diagnostico.delete()
    return JsonResponse({'success': True})