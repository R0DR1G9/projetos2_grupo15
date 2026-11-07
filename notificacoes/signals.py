from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from mensagens.models import Mensagem
from rede_social.models import Comentario, nome_do_usuario

from .servicos import notificar, notificar_mensagem


@receiver(post_save, sender=Comentario)
def avisar_comentario(sender, instance, created, **kwargs):
    if not created or instance.autor_id == instance.post.autor_id:
        return
    nome = nome_do_usuario(instance.autor)
    notificar(instance.post.autor, "comentario", f"{nome} comentou na sua publicação", instance.post.get_absolute_url())


@receiver(post_save, sender=Mensagem)
def avisar_mensagem(sender, instance, created, **kwargs):
    if not created:
        return
    destinatario = instance.conversa.outro_de(instance.remetente)
    nome = nome_do_usuario(instance.remetente)
    link = reverse("mensagens:conversa", args=[instance.remetente.get_username()])
    notificar_mensagem(destinatario, f"Nova mensagem de {nome}", link)
