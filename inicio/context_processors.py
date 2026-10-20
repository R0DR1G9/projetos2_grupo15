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

    match = request.resolver_match
    return {
        'empresa_nome': empresa,
        'usuario_nome': usuario,
        'rota_atual': match.url_name if match else '',
    }