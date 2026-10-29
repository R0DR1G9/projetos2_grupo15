# Fotos nos posts - o que falta fora do app `rede_social`

## 1. Dependência e migração
```bash
pip install Pillow
python manage.py makemigrations rede_social
python manage.py migrate
```

## 2. `settings.py` do projeto
```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

## 3. `urls.py` raiz do projeto (apenas em desenvolvimento)
```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... suas rotas ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
Em produção, sirva `MEDIA_ROOT` pelo Nginx ou use S3/Cloud Storage (`django-storages`).

## 4. Template do feed (formulário de novo post)
O `<form>` **precisa** de `enctype`, senão o arquivo não chega ao Django:
```django
<form method="post" enctype="multipart/form-data" class="rs-composer">
  {% csrf_token %}
  {{ form.conteudo }}
  {{ form.conteudo.errors }}

  <div class="rs-composer-acoes">
    {{ form.pilar }}

    <label class="rs-upload">
      <span>📷 Foto</span>
      {{ form.imagem }}
    </label>
    <button type="submit" class="rs-btn">Publicar</button>
  </div>
  {{ form.imagem.errors }}

  <div class="rs-preview" hidden>
    <img alt="Pré-visualização da imagem">
    <button type="button" class="rs-preview-remover" aria-label="Remover imagem">✕</button>
  </div>
</form>

<script>
  (function () {
    const input = document.querySelector(".rs-composer input[type=file]");
    const box = document.querySelector(".rs-preview");
    const img = box.querySelector("img");
    input.addEventListener("change", () => {
      const f = input.files[0];
      if (!f) { box.hidden = true; return; }
      img.src = URL.createObjectURL(f);
      box.hidden = false;
    });
    box.querySelector("button").addEventListener("click", () => {
      input.value = ""; box.hidden = true;
    });
  })();
</script>
```

## 5. Template do card do post (feed, detalhe, perfil, hashtag, busca)
Dentro do card, logo abaixo do texto. Use `p.alvo` - assim o repost mostra a foto do original:
```django
{% if p.alvo.imagem %}
  <a href="{{ p.alvo.imagem.url }}" target="_blank" rel="noopener" class="rs-post-imagem">
    <img src="{{ p.alvo.imagem.url }}" loading="lazy"
         alt="Imagem publicada por {{ p.alvo.autor.get_username }}">
  </a>
{% endif %}
```
No `detalhe_post.html` a variável do post é `p` (e `p.alvo = p`), então o mesmo trecho funciona.

## 6. CSS (`rede_social.css`, com escopo `.rs`)
```css
.rs .rs-upload { cursor: pointer; }
.rs .rs-upload input[type=file] { display: none; }
.rs .rs-post-imagem { display: block; margin-top: .75rem; }
.rs .rs-post-imagem img {
  width: 100%; max-height: 480px; object-fit: cover;
  border-radius: 12px; display: block;
}
.rs .rs-preview { position: relative; margin-top: .75rem; }
.rs .rs-preview img { max-width: 100%; max-height: 260px; border-radius: 12px; }
.rs .rs-preview-remover {
  position: absolute; top: 8px; right: 8px; border: 0; border-radius: 50%;
  width: 28px; height: 28px; background: rgba(0,0,0,.6); color: #fff; cursor: pointer;
}
```
