from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Count, Exists, IntegerField, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import ComentarioForm, PerfilForm, PostForm
from .models import Comentario, Curtida, Hashtag, Perfil, Pilar, Post, Seguimento

User = get_user_model()

POSTS_POR_PAGINA = 15
PILARES_VALIDOS = {valor for valor, _ in Pilar.choices}


# --------------------------------------------------------------------------- helpers
def _contagem(modelo, campo):
    """Subquery que conta linhas de `modelo` ligadas ao post (evita JOINs multiplicados)."""
    sub = (
        modelo.objects.filter(**{campo: OuterRef("pk")})
        .order_by()
        .values(campo)
        .annotate(total=Count("pk"))
        .values("total")
    )
    return Coalesce(Subquery(sub, output_field=IntegerField()), 0)


def posts_com_metricas(usuario):
    """Posts visíveis já com curtidas, comentários, reposts e estado do usuário logado."""
    return (
        Post.objects.filter(visivel=True)
        .select_related("autor", "autor__perfil_social")
        .annotate(
            total_curtidas=_contagem(Curtida, "post"),
            total_comentarios=_contagem(Comentario, "post"),
            total_reposts=_contagem(Post, "repost_de"),
            curtiu=Exists(Curtida.objects.filter(post=OuterRef("pk"), usuario=usuario)),
            repostou=Exists(Post.objects.filter(repost_de=OuterRef("pk"), autor=usuario)),
        )
    )


def preparar(pagina, usuario):
    """Define `p.alvo` (o post exibido no card). Em reposts, é o post original."""
    posts = list(pagina.object_list)
    ids = {p.repost_de_id for p in posts if p.repost_de_id}
    originais = (
        {p.pk: p for p in posts_com_metricas(usuario).filter(pk__in=ids)} if ids else {}
    )
    resultado = []
    for p in posts:
        if p.repost_de_id:
            p.alvo = originais.get(p.repost_de_id)
            if p.alvo is None:  # original oculto/removido
                continue
        else:
            p.alvo = p
        resultado.append(p)
    pagina.object_list = resultado
    return pagina


def paginar(request, queryset):
    return Paginator(queryset, POSTS_POR_PAGINA).get_page(request.GET.get("page"))


def obter_perfil(usuario):
    return Perfil.objects.get_or_create(usuario=usuario)[0]


def contexto_lateral(usuario):
    desde = timezone.now() - timedelta(days=7)
    tendencias = (
        Hashtag.objects.filter(posts__criado_em__gte=desde, posts__visivel=True)
        .annotate(total=Count("posts"))
        .order_by("-total", "nome")[:5]
    )
    sugestoes = (
        User.objects.filter(is_active=True)
        .exclude(pk=usuario.pk)
        .exclude(seguidores_social__seguidor=usuario)
        .select_related("perfil_social")
        .annotate(n_seguidores=Count("seguidores_social"))
        .order_by("-n_seguidores", "pk")[:5]
    )
    return {"tendencias": tendencias, "sugestoes": sugestoes}


def contexto(request, **extra):
    params = request.GET.copy()
    params.pop("page", None)
    ctx = {"lateral": contexto_lateral(request.user), "qs": params.urlencode()}
    ctx.update(extra)
    return ctx


def voltar(request, fallback, ancora=""):
    """Redireciona para `next` (se for seguro) ou para `fallback`."""
    destino = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(
        destino, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        destino = fallback
    destino = destino.split("#")[0]
    return redirect(f"{destino}#{ancora}" if ancora else destino)


def _eh_ajax(request):
    """Requisições feitas pelo fetch() do front (sem recarregar a página)."""
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def _usuario_ou_404(username):
    return get_object_or_404(User, is_active=True, **{User.USERNAME_FIELD: username})


# --------------------------------------------------------------------------- feed
@login_required
def feed(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            post.save()
            messages.success(request, "Publicação criada com sucesso.")
            return redirect("rede_social:feed")
    else:
        form = PostForm()

    aba = request.GET.get("aba", "todos")
    pilar = request.GET.get("pilar", "")
    qs = posts_com_metricas(request.user)

    if aba == "seguindo":
        seguidos = Seguimento.objects.filter(seguidor=request.user).values("seguido_id")
        qs = qs.filter(Q(autor_id__in=seguidos) | Q(autor=request.user))
    elif aba == "empresa":
        empresa = obter_perfil(request.user).empresa
        if empresa:
            qs = qs.filter(autor__perfil_social__empresa__iexact=empresa)
        else:
            qs = qs.none()
    else:
        aba = "todos"

    if pilar in PILARES_VALIDOS:
        qs = qs.filter(pilar=pilar)
    else:
        pilar = ""

    pagina = preparar(paginar(request, qs), request.user)
    return render(
        request,
        "rede_social/feed.html",
        contexto(request, form=form, page=pagina, aba=aba, pilar=pilar, pilares=Pilar.choices),
    )


# --------------------------------------------------------------------------- posts
@login_required
def detalhe_post(request, pk):
    post = get_object_or_404(posts_com_metricas(request.user), pk=pk)
    if post.repost_de_id:
        return redirect("rede_social:detalhe_post", pk=post.repost_de_id)
    post.alvo = post

    if request.method == "POST":
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.post = post
            comentario.autor = request.user
            comentario.save()
            messages.success(request, "Comentário publicado.")
            return redirect(f"{reverse('rede_social:detalhe_post', args=[pk])}#comentarios")
    else:
        form = ComentarioForm()

    comentarios = post.comentarios.select_related("autor", "autor__perfil_social")
    return render(
        request,
        "rede_social/detalhe_post.html",
        contexto(request, p=post, form=form, comentarios=comentarios),
    )


@login_required
@require_POST
def curtir(request, pk):
    post = get_object_or_404(Post, pk=pk, visivel=True)
    curtida, criada = Curtida.objects.get_or_create(post=post, usuario=request.user)
    if not criada:
        curtida.delete()
    if _eh_ajax(request):
        return JsonResponse({"curtido": criada, "total": post.curtidas.count()})
    return voltar(request, reverse("rede_social:feed"), f"post-{post.pk}")


@login_required
@require_POST
def repostar(request, pk):
    original = get_object_or_404(Post, pk=pk, visivel=True, repost_de__isnull=True)
    if original.autor_id == request.user.id:
        messages.error(request, "Você não pode repostar a sua própria publicação.")
    else:
        repost, criado = Post.objects.get_or_create(
            autor=request.user, repost_de=original, defaults={"conteudo": ""}
        )
        if criado:
            messages.success(request, "Publicação repostada.")
        else:
            repost.delete()
            messages.info(request, "Repost removido.")
    return voltar(request, reverse("rede_social:feed"), f"post-{original.pk}")


@login_required
@require_POST
def excluir_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.autor_id != request.user.id and not request.user.is_staff:
        raise PermissionDenied
    post.delete()
    messages.success(request, "Publicação excluída.")
    return voltar(request, reverse("rede_social:feed"))


# --------------------------------------------------------------------------- descoberta
@login_required
def hashtag(request, tag):
    tag_obj = get_object_or_404(Hashtag, nome=tag.lower())
    qs = posts_com_metricas(request.user).filter(hashtags=tag_obj)
    pagina = preparar(paginar(request, qs), request.user)
    return render(
        request, "rede_social/hashtag.html", contexto(request, tag=tag_obj, page=pagina)
    )


@login_required
def buscar(request):
    q = request.GET.get("q", "").strip()
    pagina, pessoas = None, []
    if q:
        qs = posts_com_metricas(request.user).filter(
            repost_de__isnull=True, conteudo__icontains=q
        )
        pagina = preparar(paginar(request, qs), request.user)
        pessoas = (
            User.objects.filter(is_active=True)
            .filter(
                Q(**{f"{User.USERNAME_FIELD}__icontains": q})
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(perfil_social__nome_exibicao__icontains=q)
                | Q(perfil_social__empresa__icontains=q)
            )
            .select_related("perfil_social")
            .distinct()[:10]
        )
    return render(
        request, "rede_social/busca.html", contexto(request, q=q, page=pagina, pessoas=pessoas)
    )


# --------------------------------------------------------------------------- perfil
@login_required
def perfil(request, username):
    alvo = _usuario_ou_404(username)
    perfil_social = obter_perfil(alvo)

    aba = request.GET.get("aba", "posts")
    qs = posts_com_metricas(request.user)
    if aba == "curtidas":
        qs = qs.filter(pk__in=Curtida.objects.filter(usuario=alvo).values("post_id"))
    else:
        aba = "posts"
        qs = qs.filter(autor=alvo)

    pagina = preparar(paginar(request, qs), request.user)
    return render(
        request,
        "rede_social/perfil.html",
        contexto(
            request,
            alvo=alvo,
            perfil_social=perfil_social,
            aba=aba,
            page=pagina,
            seguindo=Seguimento.objects.filter(seguidor=request.user, seguido=alvo).exists(),
            total_seguidores=alvo.seguidores_social.count(),
            total_seguindo=alvo.seguindo_social.count(),
            total_posts=Post.objects.filter(
                autor=alvo, repost_de__isnull=True, visivel=True
            ).count(),
        ),
    )


@login_required
@require_POST
def seguir(request, username):
    alvo = _usuario_ou_404(username)
    if alvo.pk == request.user.pk:
        messages.error(request, "Você não pode seguir a si mesmo.")
    else:
        rel, criado = Seguimento.objects.get_or_create(seguidor=request.user, seguido=alvo)
        if not criado:
            rel.delete()
    return voltar(request, reverse("rede_social:perfil", args=[username]))


@login_required
def editar_perfil(request):
    perfil_social = obter_perfil(request.user)
    if request.method == "POST":
        form = PerfilForm(request.POST, instance=perfil_social)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado.")
            return redirect("rede_social:perfil", username=request.user.get_username())
    else:
        form = PerfilForm(instance=perfil_social)
    return render(request, "rede_social/perfil_form.html", contexto(request, form=form))
