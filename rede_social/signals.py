from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Perfil, Post


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def criar_perfil_social(sender, instance, created, **kwargs):
    """Todo usuário novo ganha automaticamente um perfil da rede social."""
    if created:
        Perfil.objects.get_or_create(usuario=instance)


@receiver(post_delete, sender=Post)
def remover_imagem_do_post(sender, instance, **kwargs):
    """Apaga o arquivo do disco ao excluir o post (inclusive em cascata, ex.: usuário removido).

    Roda no commit: se a transação der rollback, o arquivo continua existindo.
    """
    if instance.imagem:
        armazenamento, nome = instance.imagem.storage, instance.imagem.name
        transaction.on_commit(lambda: armazenamento.delete(nome))
