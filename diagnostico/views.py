from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import DiagnosticoForm
from .models import DiagnosticoESG

def home(request):
    diagnosticos = DiagnosticoESG.objects.all().order_by('-data_criacao')
    form = DiagnosticoForm()
    
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

@require_POST
def salvar_diagnostico(request):
    form = DiagnosticoForm(request.POST)
    if form.is_valid():
        diagnostico = form.save()
        resultados = diagnostico.calcular_pontuacao()
        return JsonResponse({
            'success': True,
            'nome_empresa': diagnostico.nome_empresa,
            'resultados': resultados
        })
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)

@require_POST
def deletar_diagnostico(request, pk):
    diagnostico = get_object_or_404(DiagnosticoESG, pk=pk)
    diagnostico.delete()
    return JsonResponse({'success': True})