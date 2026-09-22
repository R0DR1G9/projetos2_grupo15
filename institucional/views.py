from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ContatoForm


def sobre(request):
    return render(request, "institucional/sobre.html")


def quem_somos(request):
    equipe = [
        {"nome": "Rodrigo Barbosa"},
        {"nome": "Joao Miguel"},
        {"nome": "Arthur Siqueira"},
        {"nome": "Rafael Queiroz"},
        {"nome": "Fernando Sotero"},
        {"nome": "Joao Victor Moraes"},
    ]
    return render(request, "institucional/quem_somos.html", {"equipe": equipe})


def contato(request):
    if request.method == "POST":
        form = ContatoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Mensagem enviada! Nossa equipe vai dar uma olhada em breve.")
            return redirect("contato")
    else:
        form = ContatoForm()

    return render(request, "institucional/contato.html", {"form": form})
