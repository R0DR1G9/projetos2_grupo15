from django.shortcuts import render
from django.http import JsonResponse
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

def salvar_diagnostico(request):
    if request.method == 'POST':
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
    return JsonResponse({'success': False, 'message': 'Método inválido'}, status=405)