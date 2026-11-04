from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Conteudo

CATEGORIAS_VALIDAS = dict(Conteudo.CATEGORIAS)


@login_required
def lista(request):
    categoria = request.GET.get('categoria', '')
    conteudos = Conteudo.objects.filter(publicado=True)
    if categoria in CATEGORIAS_VALIDAS:
        conteudos = conteudos.filter(categoria=categoria)
    else:
        categoria = ''
    return render(request, 'biblioteca/lista.html', {
        'conteudos': conteudos,
        'categorias': Conteudo.CATEGORIAS,
        'categoria': categoria,
    })


@login_required
def detalhe(request, pk):
    conteudo = get_object_or_404(Conteudo, pk=pk, publicado=True)
    return render(request, 'biblioteca/detalhe.html', {'conteudo': conteudo})
