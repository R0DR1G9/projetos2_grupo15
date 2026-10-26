import logging
import mimetypes
import os
from urllib.parse import quote

from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from vercel.blob import sync as blob
from vercel.blob.errors import BlobError

logger = logging.getLogger(__name__)

PREFIXO_TOKEN = "vercel_blob_rw_"
CACHE_UM_ANO = 365 * 24 * 60 * 60


def id_da_loja():
    token = os.environ.get("BLOB_READ_WRITE_TOKEN", "").strip()
    if not token.startswith(PREFIXO_TOKEN):
        raise ImproperlyConfigured("BLOB_READ_WRITE_TOKEN ausente ou em formato inválido.")
    identificador = token[len(PREFIXO_TOKEN):].partition("_")[0].lower()
    if not identificador:
        raise ImproperlyConfigured("BLOB_READ_WRITE_TOKEN em formato inválido.")
    return identificador


@deconstructible
class VercelBlobStorage(Storage):
    def _save(self, name, content):
        content.seek(0)
        resultado = blob.put_blob(
            name,
            content.read(),
            access="public",
            content_type=mimetypes.guess_type(name)[0] or "application/octet-stream",
            cache_control_max_age=CACHE_UM_ANO,
        )
        return resultado.pathname

    def _open(self, name, mode="rb"):
        return ContentFile(blob.get_blob(name, access="public").body, name=name)

    def delete(self, name):
        if not name:
            return
        try:
            blob.delete_blob(self.url(name))
        except (BlobError, ImproperlyConfigured):
            logger.warning("Não foi possível apagar %s do Vercel Blob.", name, exc_info=True)

    def exists(self, name):
        return False

    def size(self, name):
        return blob.head_blob(name).size

    def url(self, name):
        return f"https://{id_da_loja()}.public.blob.vercel-storage.com/{quote(name.lstrip('/'), safe='/')}"
