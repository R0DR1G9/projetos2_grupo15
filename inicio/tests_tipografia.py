from django.test import TestCase
from django.urls import reverse


class TipografiaTests(TestCase):
    def test_pagina_carrega_as_tres_familias_e_o_css_de_tipografia(self):
        html = self.client.get(reverse('sobre')).content.decode()
        self.assertIn('family=Inter:', html)
        self.assertIn('family=Manrope:', html)
        self.assertIn('api.fontshare.com/v2/css?f[]=satoshi', html)
        self.assertIn('css/tipografia.css', html)
        self.assertNotIn('Nunito', html)

    def test_css_de_tipografia_e_servido(self):
        resp = self.client.get('/static/css/tipografia.css')
        self.assertEqual(resp.status_code, 200)

    def test_hierarquia_definida_no_css(self):
        with open('static/css/tipografia.css', encoding='utf-8') as arquivo:
            css = arquivo.read()
        for trecho in (
            "--fonte-titulo: 'Satoshi'",
            "--fonte-apoio: 'Manrope'",
            "--fonte-corpo: 'Inter'",
            'font-size: 1.75rem !important',
            'font-size: 1.375rem !important',
            'font-size: .875rem',
            'font-size: .75rem',
        ):
            self.assertIn(trecho, css)

    def test_nenhuma_folha_de_estilo_usa_nunito(self):
        import pathlib
        for caminho in pathlib.Path('static/css').glob('*.css'):
            self.assertNotIn('Nunito', caminho.read_text(encoding='utf-8'), caminho.name)
