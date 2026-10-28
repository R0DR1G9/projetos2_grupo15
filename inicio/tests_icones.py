import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class IconesCoolIconsTests(SimpleTestCase):
    def arquivos(self, padroes):
        base = Path(settings.BASE_DIR)
        achados = []
        for padrao in padroes:
            achados += [p for p in base.rglob(padrao) if "staticfiles" not in p.parts and "venv" not in p.parts]
        return achados

    def test_nao_usa_mais_bootstrap_icons(self):
        for arquivo in self.arquivos(["*.html", "*.js"]):
            texto = arquivo.read_text(encoding="utf-8")
            self.assertNotIn("bootstrap-icons", texto, arquivo)
            self.assertIsNone(re.search(r"\bbi bi-", texto), arquivo)

    def test_todo_icone_usado_tem_svg_e_regra_css(self):
        base = Path(settings.BASE_DIR)
        css = (base / "static" / "css" / "icones.css").read_text(encoding="utf-8")
        usados = set()
        for arquivo in self.arquivos(["*.html", "*.js", "views.py"]):
            usados |= set(re.findall(r"\bci-([a-z0-9-]+)", arquivo.read_text(encoding="utf-8")))
        self.assertTrue(usados)
        for nome in usados:
            self.assertIn(f".ci-{nome} ", css, nome)
            self.assertTrue((base / "static" / "icones" / f"{nome}.svg").exists(), nome)
