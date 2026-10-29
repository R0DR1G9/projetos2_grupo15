from django.conf import settings
from django.db import models


class Empresa(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='empresa')
    cnpj = models.CharField(max_length=14, unique=True, verbose_name='CNPJ')

    def __str__(self):
        return f'{self.usuario.first_name} ({self.cnpj_formatado})'

    @property
    def cnpj_formatado(self):
        c = self.cnpj
        return f'{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}'
