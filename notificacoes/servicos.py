from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from atividades.models import Atividade

from .models import Notificacao

DIAS_DE_ANTECEDENCIA = 3


def notificar(usuario, tipo, texto, link="", chave=""):
    dados = {"tipo": tipo, "texto": texto[:200], "link": link}
    if chave:
        return Notificacao.objects.get_or_create(usuario=usuario, chave=chave, defaults=dados)[0]
    return Notificacao.objects.create(usuario=usuario, **dados)


def notificar_mensagem(destinatario, texto, link):
    pendente = Notificacao.objects.filter(usuario=destinatario, tipo="mensagem", link=link, lida=False)
    if pendente.exists():
        pendente.update(texto=texto[:200], criada_em=timezone.now())
        return
    notificar(destinatario, "mensagem", texto, link)


def sincronizar_prazos(usuario):
    limite = timezone.localdate() + timedelta(days=DIAS_DE_ANTECEDENCIA)
    pendentes = Atividade.objects.filter(usuario=usuario, prazo__isnull=False, prazo__lte=limite).exclude(status="concluido")
    for atividade in pendentes:
        chave = f"prazo:{atividade.pk}:{atividade.prazo:%Y%m%d}:{atividade.situacao_prazo}"
        notificar(
            usuario,
            "prazo",
            f"{atividade.titulo} - {atividade.rotulo_prazo}",
            reverse("quadro_atividades"),
            chave,
        )
