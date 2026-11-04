import re

from django.core.exceptions import ValidationError
from django.db import models

PADRAO_YOUTUBE = re.compile(r'(?:youtu\.be/|youtube\.com/(?:watch\?(?:.*&)?v=|embed/|shorts/))([A-Za-z0-9_-]{11})')


class Conteudo(models.Model):
    CATEGORIAS = [
        ('ambiental', 'Ambiental'),
        ('social', 'Social'),
        ('governanca', 'Governança'),
    ]
    TIPOS = [
        ('video', 'Vídeo'),
        ('texto', 'Texto'),
    ]

    titulo = models.CharField(max_length=150, verbose_name='Título')
    descricao = models.CharField(max_length=300, verbose_name='Resumo')
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, verbose_name='Categoria')
    tipo = models.CharField(max_length=10, choices=TIPOS, default='texto', verbose_name='Tipo')
    link_video = models.URLField(blank=True, verbose_name='Link do vídeo no YouTube')
    texto = models.TextField(blank=True, verbose_name='Texto do tutorial')
    publicado = models.BooleanField(default=True, verbose_name='Publicado')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['categoria', 'titulo']
        verbose_name = 'Conteúdo'
        verbose_name_plural = 'Conteúdos'

    def __str__(self):
        return f'{self.titulo} ({self.get_tipo_display()})'

    @property
    def id_youtube(self):
        achado = PADRAO_YOUTUBE.search(self.link_video or '')
        return achado.group(1) if achado else ''

    def clean(self):
        if self.link_video and not self.id_youtube:
            raise ValidationError({'link_video': 'Informe um link válido do YouTube.'})
