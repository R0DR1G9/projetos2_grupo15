from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CadastroForm


def cadastro(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = CadastroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('home')
    return render(request, 'contas/cadastro.html', {'form': form})


@login_required
def perfil(request):
    user = request.user
    empresa = getattr(user, 'empresa', None)   # contas antigas podem não ter CNPJ
    diagnosticos = user.diagnosticos.order_by('-data_criacao')
    ultimo = diagnosticos.first()
    return render(request, 'contas/perfil.html', {
        'empresa': empresa,
        'total_diagnosticos': diagnosticos.count(),
        'ultimo': ultimo,
        'pontuacao': ultimo.calcular_pontuacao() if ultimo else None,
    })