import io

from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image, ImageOps

LADO_MAXIMO = 1600
QUALIDADE = 85
FORMATOS_REDUZIVEIS = {"JPEG", "PNG", "WEBP"}


def reduzir_imagem(arquivo, lado_maximo=LADO_MAXIMO):
    arquivo.seek(0)
    imagem = Image.open(arquivo)
    formato = imagem.format
    if (
        formato not in FORMATOS_REDUZIVEIS
        or getattr(imagem, "is_animated", False)
        or max(imagem.size) <= lado_maximo
    ):
        arquivo.seek(0)
        return arquivo

    imagem = ImageOps.exif_transpose(imagem)
    imagem.thumbnail((lado_maximo, lado_maximo), Image.LANCZOS)

    opcoes = {}
    if formato == "JPEG":
        if imagem.mode not in ("RGB", "L"):
            imagem = imagem.convert("RGB")
        opcoes = {"quality": QUALIDADE, "optimize": True}
    elif formato == "WEBP":
        opcoes = {"quality": QUALIDADE}
    else:
        opcoes = {"optimize": True}

    saida = io.BytesIO()
    imagem.save(saida, format=formato, **opcoes)
    tamanho = saida.tell()
    saida.seek(0)
    return InMemoryUploadedFile(
        saida, "imagem", arquivo.name, getattr(arquivo, "content_type", None), tamanho, None
    )
