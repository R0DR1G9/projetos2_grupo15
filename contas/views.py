from django.shortcuts import render

# Create your views here.
from django.contrib.auth import login
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