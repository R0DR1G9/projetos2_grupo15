from django.core.exceptions import ObjectDoesNotExist

from setup.versao import VERSAO


def layout(request):
    """Dados que o layout (barra lateral e topo) usa em TODAS as páginas."""
    user = request.user
    if user.is_authenticated:
        nome = user.first_name.strip() or user.username
        empresa = nome
        usuario = nome
    else:
        empresa = 'Plataforma ESG'
        usuario = 'Visitante'

    foto = ''
    if user.is_authenticated:
        try:
            if user.perfil_social.foto:
                foto = user.perfil_social.foto.url
        except ObjectDoesNotExist:
            pass

    match = request.resolver_match
    return {
        'empresa_nome': empresa,
        'usuario_nome': usuario,
        'usuario_foto': foto,
        'rota_atual': match.url_name if match else '',
        'versao_vastra': VERSAO,
    }