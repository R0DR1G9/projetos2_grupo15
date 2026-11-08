from django.contrib import messages
from django.contrib.staticfiles import finders
from django.shortcuts import redirect, render

from .forms import ContatoForm


def sobre(request):
    return render(request, "institucional/sobre.html")


EQUIPE = [
    ("Rodrigo Barbosa", "rodrigo"),
    ("Ana Beatriz Pedrosa", "ana-beatriz"),
    ("Fernando Antônio Fernandes Sotero", "fernando"),
    ("João Miguel Ramos Galvão Couto", "joao-miguel"),
    ("João Victor Moraes Pimentel", "joao-victor"),
    ("Arthur Guedes Siqueira", "arthur"),
    ("Maria Clara Angeiras Morato de Souza", "maria-clara"),
    ("Marina Pontes Xavier", "marina"),
    ("Daniel", "daniel"),
    ("Paulo", "paulo"),
    ("Rafael Queiroz", "rafael"),
]


def quem_somos(request):
    equipe = []
    for nome, slug in EQUIPE:
        caminho = f"img/equipe/{slug}.jpg"
        equipe.append({"nome": nome, "foto": caminho if finders.find(caminho) else None})
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
