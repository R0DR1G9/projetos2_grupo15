# Mensagens (Direct) - como ligar ao projeto

Depende do app `rede_social` (nomes e perfis) e do seu `templates/base.html` (blocos `title`, `extra_head`, `content`, `extra_scripts`).

## 1. `settings.py`
```python
INSTALLED_APPS = [
    # ...
    "rede_social",
    "mensagens",
]

TEMPLATES = [{
    # ...
    "OPTIONS": {"context_processors": [
        # ... os que já existem ...
        "mensagens.context_processors.nao_lidas",   # selo de não lidas no menu
    ]},
}]
```

## 2. `urls.py` do projeto
```python
path("mensagens/", include("mensagens.urls")),
```

## 3. Banco
```bash
python manage.py migrate
```

## 4. Aba "Mensagens" no menu lateral (`templates/base.html`)
Logo abaixo do item "Rede Social":
```django
<a class="menu-item {% if request.resolver_match.app_name == 'mensagens' %}ativo{% endif %}" href="{% url 'mensagens:caixa' %}"{% if request.resolver_match.app_name == 'mensagens' %} aria-current="page"{% endif %}><i class="bi bi-send"></i><span>Mensagens</span>{% if mensagens_nao_lidas %}<b style="margin-left:auto;min-width:20px;height:20px;padding:0 6px;border-radius:999px;background:#ffc20e;color:#2b2a22;font-size:12px;font-weight:800;line-height:20px;text-align:center">{{ mensagens_nao_lidas }}</b>{% endif %}</a>
```

## 5. Botão "Mensagem" no perfil (opcional) - `rede_social/templates/rede_social/perfil.html`
Ao lado do botão Seguir (dentro do `{% else %}` de `alvo == request.user`):
```django
<a class="rs-btn rs-btn-sec" href="{% url 'mensagens:conversa' alvo|login_usuario %}">Mensagem</a>
```
