from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, IntegerField, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import MensagemForm
from .models import Conversa, Mensagem

User = get_user_model()

MENSAGENS_POR_PAGINA = 50
MENSAGENS_MAXIMO = 500


# --------------------------------------------------------------------------- helpers
def _eh_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def _usuario_ou_404(username):
    return get_object_or_404(User, is_active=True, **{User.USERNAME_FIELD: username})


def _rotulo(momento):
    """Hora de hoje, dia/mês neste ano, ou dia/mês/ano."""
    momento, hoje = timezone.localtime(momento), timezone.localdate()
    if momento.date() == hoje:
        return momento.strftime("%H:%M")
    if momento.year == hoje.year:
        return momento.strftime("%d/%m")
    return momento.strftime("%d/%m/%y")


def _com_perfil(campos):
    """Evita uma consulta por conversa se o app rede_social estiver instalado."""
    return [f"{c}__perfil_social" for c in campos] if hasattr(User, "perfil_social") else []


def _conversas(eu):
    """Conversas do usuário que já têm mensagens, da mais recente para a mais antiga."""
    ultima = Mensagem.objects.filter(conversa=OuterRef("pk")).order_by("-criada_em", "-pk")
    nao_lidas = (
        Mensagem.objects.filter(conversa=OuterRef("pk"), lida_em__isnull=True)
        .exclude(remetente=eu)
        .order_by()
        .values("conversa")
        .annotate(n=Count("pk"))
        .values("n")
    )
    qs = (
        Conversa.do_usuario(eu)
        .select_related("usuario_a", "usuario_b", *_com_perfil(["usuario_a", "usuario_b"]))
        .annotate(
            ultima_texto=Subquery(ultima.values("texto")[:1]),
            ultima_em=Subquery(ultima.values("criada_em")[:1]),
            ultima_de_id=Subquery(ultima.values("remetente_id")[:1]),
            nao_lidas=Coalesce(Subquery(nao_lidas, output_field=IntegerField()), 0),
        )
        .filter(ultima_em__isnull=False)
        .order_by("-ultima_em", "-pk")
    )
    conversas = list(qs)
    for c in conversas:
        c.outro = c.outro_de(eu)
        c.rotulo = _rotulo(c.ultima_em)
    return conversas


def _buscar_pessoas(eu, q):
    filtro = (
        Q(**{f"{User.USERNAME_FIELD}__icontains": q})
        | Q(first_name__icontains=q)
        | Q(last_name__icontains=q)
    )
    if hasattr(User, "perfil_social"):
        filtro |= Q(perfil_social__nome_exibicao__icontains=q) | Q(perfil_social__empresa__icontains=q)
    return (
        User.objects.filter(is_active=True)
        .exclude(pk=eu.pk)
        .filter(filtro)
        .select_related(*(["perfil_social"] if hasattr(User, "perfil_social") else []))
        .distinct()[:10]
    )


def _contexto(request, **extra):
    q = request.GET.get("q", "").strip()
    ctx = {
        "eu": request.user,
        "q": q,
        "pessoas": _buscar_pessoas(request.user, q) if q else [],
        "conversas": _conversas(request.user),
    }
    ctx.update(extra)
    return ctx


def _status(ultima, eu):
    """'Visto'/'Enviado' sob a última mensagem, se ela for minha."""
    if ultima is None or ultima.remetente_id != eu.pk:
        return ""
    return "Visto" if ultima.lida_em else "Enviado"


def _marcar_lidas(conversa, eu):
    Mensagem.objects.filter(conversa=conversa, lida_em__isnull=True).exclude(remetente=eu).update(
        lida_em=timezone.now()
    )


def _html(mensagens, eu):
    return render_to_string("mensagens/_bolhas.html", {"mensagens": mensagens, "eu": eu})


# --------------------------------------------------------------------------- telas
@login_required
def caixa(request):
    """Lista de conversas (e busca de pessoas para começar uma nova)."""
    return render(request, "mensagens/caixa.html", _contexto(request))


@login_required
def conversa(request, username):
    eu = request.user
    outro = _usuario_ou_404(username)
    if outro.pk == eu.pk:
        messages.info(request, "Escolha outra pessoa para conversar.")
        return redirect("mensagens:caixa")

    conv = Conversa.entre(eu, outro)
    voltar_para = reverse("mensagens:conversa", args=[username])

    if request.method == "POST":
        form = MensagemForm(request.POST)
        if form.is_valid():
            conv = conv or Conversa.entre(eu, outro, criar=True)
            msg = Mensagem.objects.create(conversa=conv, remetente=eu, texto=form.cleaned_data["texto"])
            if _eh_ajax(request):
                return JsonResponse({"id": msg.pk, "html": _html([msg], eu), "status": _status(msg, eu)})
            return redirect(f"{voltar_para}#ms-fim")
        if _eh_ajax(request):
            erro = " ".join(form.errors.get("texto", ["Mensagem inválida."]))
            return JsonResponse({"erro": erro}, status=400)
    else:
        form = MensagemForm()

    try:
        limite = min(max(int(request.GET.get("limite", MENSAGENS_POR_PAGINA)), 1), MENSAGENS_MAXIMO)
    except ValueError:
        limite = MENSAGENS_POR_PAGINA

    mensagens, tem_mais = [], False
    if conv:
        _marcar_lidas(conv, eu)  # abrir a conversa marca as recebidas como lidas
        recentes = list(conv.mensagens.order_by("-criada_em", "-pk")[: limite + 1])
        tem_mais = len(recentes) > limite
        mensagens = list(reversed(recentes[:limite]))

    ultima = mensagens[-1] if mensagens else None
    return render(
        request,
        "mensagens/conversa.html",
        _contexto(
            request,
            outro=outro,
            form=form,
            mensagens=mensagens,
            tem_mais=tem_mais,
            limite_proximo=min(limite + MENSAGENS_POR_PAGINA, MENSAGENS_MAXIMO),
            ultima_id=ultima.pk if ultima else 0,
            status=_status(ultima, eu),
        ),
    )


@login_required
def novas(request, username):
    """Consulta (polling) feita pelo JS: mensagens novas desde `?depois=<id>`."""
    eu = request.user
    outro = _usuario_ou_404(username)
    conv = Conversa.entre(eu, outro)
    if conv is None:
        return JsonResponse({"html": "", "ultima": 0, "status": ""})

    try:
        depois = int(request.GET.get("depois", 0))
    except ValueError:
        depois = 0

    novas_msgs = list(conv.mensagens.filter(pk__gt=depois))
    _marcar_lidas(conv, eu)
    ultima = conv.mensagens.order_by("-criada_em", "-pk").first()
    return JsonResponse(
        {
            "html": _html(novas_msgs, eu),
            "ultima": ultima.pk if ultima else 0,
            "status": _status(ultima, eu),
        }
    )


@login_required
@require_POST
def excluir(request, pk):
    """Desfazer envio: só quem enviou pode apagar a própria mensagem."""
    msg = get_object_or_404(Mensagem.objects.select_related("conversa"), pk=pk)
    if msg.remetente_id != request.user.pk:
        raise Http404
    outro = msg.conversa.outro_de(request.user)
    msg.delete()
    if _eh_ajax(request):
        return JsonResponse({"ok": True})
    return redirect("mensagens:conversa", username=outro.get_username())
