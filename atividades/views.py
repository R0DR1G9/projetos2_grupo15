from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AtividadeForm
from .models import Atividade


@login_required
def quadro(request):
    if request.method == "POST":
        form = AtividadeForm(request.POST)
        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.usuario = request.user
            atividade.save()
            messages.success(request, "Atividade adicionada em \"Aguardando início\".")
            return redirect("quadro_atividades")
    else:
        form = AtividadeForm()

    atividades = Atividade.objects.filter(usuario=request.user)
    colunas = [
        {
            "chave": chave,
            "nome": nome,
            "atividades": [a for a in atividades if a.status == chave],
        }
        for chave, nome in Atividade.STATUS
    ]
    return render(request, "atividades/quadro.html", {
        "form": form,
        "colunas": colunas,
        "status_opcoes": Atividade.STATUS,
    })


@login_required
@require_POST
def mudar_status(request, pk):
    atividade = get_object_or_404(Atividade, pk=pk, usuario=request.user)
    novo_status = request.POST.get("status")
    if novo_status in dict(Atividade.STATUS):
        atividade.status = novo_status
        atividade.save(update_fields=["status"])
    else:
        messages.error(request, "Status inválido.", extra_tags="danger")
    return redirect("quadro_atividades")


@login_required
@require_POST
def deletar(request, pk):
    get_object_or_404(Atividade, pk=pk, usuario=request.user).delete()
    messages.success(request, "Atividade removida.")
    return redirect("quadro_atividades")
