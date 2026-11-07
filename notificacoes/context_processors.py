from .servicos import sincronizar_prazos

LIMITE_NO_SINO = 5


def sino(request):
    usuario = getattr(request, "user", None)
    if usuario is None or not usuario.is_authenticated:
        return {}
    sincronizar_prazos(usuario)
    return {
        "notificacoes_nao_lidas": usuario.notificacoes.filter(lida=False).count(),
        "notificacoes_recentes": list(usuario.notificacoes.all()[:LIMITE_NO_SINO]),
    }
