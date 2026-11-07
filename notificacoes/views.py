from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Notificacao

LIMITE_NA_LISTA = 50


@login_required
def lista(request):
    return render(request, "notificacoes/lista.html", {"notificacoes": request.user.notificacoes.all()[:LIMITE_NA_LISTA]})


@login_required
def abrir(request, pk):
    notificacao = get_object_or_404(Notificacao, pk=pk, usuario=request.user)
    if not notificacao.lida:
        notificacao.lida = True
        notificacao.save(update_fields=["lida"])
    return redirect(notificacao.link or "notificacoes:lista")


@login_required
@require_POST
def marcar_todas(request):
    request.user.notificacoes.filter(lida=False).update(lida=True)
    messages.success(request, "Todas as notificações foram marcadas como lidas.")
    return redirect("notificacoes:lista")
