from django import template
from django.urls import reverse
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe

from ..models import HASHTAG_RE, nome_do_usuario

register = template.Library()


@register.filter
def nome_usuario(usuario):
    return nome_do_usuario(usuario)


@register.filter
def login_usuario(usuario):
    return usuario.get_username()


@register.filter
def iniciais(usuario):
    partes = nome_do_usuario(usuario).split()
    if not partes:
        return "?"
    letras = partes[0][0] + (partes[-1][0] if len(partes) > 1 else "")
    return letras.upper()


@register.filter(needs_autoescape=True)
def linkificar(texto, autoescape=True):
    """Escapa o HTML, transforma #hashtags em links e preserva quebras de linha."""
    texto = conditional_escape(texto) if autoescape else str(texto)

    def trocar(m):
        tag = m.group(1)
        return format_html(
            '<a class="hashtag" href="{}">#{}</a>',
            reverse("rede_social:hashtag", args=[tag.lower()]),
            tag,
        )

    return mark_safe(HASHTAG_RE.sub(trocar, str(texto)).replace("\n", "<br>"))
