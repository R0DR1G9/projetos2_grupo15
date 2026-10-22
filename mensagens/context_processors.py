from django.db.models import Q

from .models import Mensagem


def nao_lidas(request):
    """Disponibiliza `mensagens_nao_lidas` (número) para o selo no menu lateral."""
    usuario = getattr(request, "user", None)
    if usuario is None or not usuario.is_authenticated:
        return {}
    total = (
        Mensagem.objects.filter(lida_em__isnull=True)
        .filter(Q(conversa__usuario_a=usuario) | Q(conversa__usuario_b=usuario))
        .exclude(remetente=usuario)
        .count()
    )
    return {"mensagens_nao_lidas": total}
