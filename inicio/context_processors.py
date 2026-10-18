from django.conf import settings

from diagnostico.models import DiagnosticoESG


def layout(request):
    """Dados que o layout (barra lateral e topo) usa em TODAS as páginas.

    Como ainda não existe login, o nome da empresa vem do diagnóstico mais
    recente e o nome do usuário vem de USUARIO_NOME, em setup/settings.py.
    """
    ultimo = DiagnosticoESG.objects.order_by('-data_criacao').first()
    match = request.resolver_match
    return {
        'empresa_nome': ultimo.nome_empresa.strip() if ultimo else 'Sua empresa',
        'usuario_nome': getattr(settings, 'USUARIO_NOME', 'Gestor(a)'),
        'rota_atual': match.url_name if match else '',
    }
