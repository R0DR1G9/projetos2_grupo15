from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Conteudo


class BibliotecaTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('gestora', password='senha-forte-123', first_name='Aurora')
        self.client.force_login(self.user)
        Conteudo.objects.all().delete()
        self.amb = Conteudo.objects.create(titulo='Reaproveitar retalhos', descricao='r', categoria='ambiental', tipo='video',
                                           link_video='https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        self.soc = Conteudo.objects.create(titulo='Equipe segura', descricao='s', categoria='social', tipo='texto', texto='Conteudo do texto')
        self.oculto = Conteudo.objects.create(titulo='Rascunho', descricao='x', categoria='social', publicado=False)

    def test_exige_login(self):
        self.client.logout()
        r = self.client.get(reverse('biblioteca'))
        self.assertEqual(r.status_code, 302)

    def test_lista_mostra_titulo_categoria_e_tipo(self):
        r = self.client.get(reverse('biblioteca'))
        self.assertContains(r, 'Reaproveitar retalhos')
        self.assertContains(r, 'Ambiental')
        self.assertContains(r, 'Vídeo')
        self.assertContains(r, 'Texto')
        self.assertNotContains(r, 'Rascunho')

    def test_filtra_por_categoria(self):
        r = self.client.get(reverse('biblioteca'), {'categoria': 'ambiental'})
        self.assertContains(r, 'Reaproveitar retalhos')
        self.assertNotContains(r, 'Equipe segura')

    def test_categoria_invalida_mostra_todos(self):
        r = self.client.get(reverse('biblioteca'), {'categoria': 'xyz'})
        self.assertContains(r, 'Reaproveitar retalhos')
        self.assertContains(r, 'Equipe segura')

    def test_video_abre_com_player_incorporado(self):
        r = self.client.get(reverse('biblioteca_detalhe', args=[self.amb.pk]))
        self.assertContains(r, 'youtube-nocookie.com/embed/dQw4w9WgXcQ')

    def test_video_sem_link_avisa_que_vem_em_breve(self):
        sem = Conteudo.objects.create(titulo='Sem link', descricao='d', categoria='social', tipo='video')
        r = self.client.get(reverse('biblioteca_detalhe', args=[sem.pk]))
        self.assertContains(r, 'será publicado em breve')
        self.assertNotContains(r, '<iframe')

    def test_texto_abre_com_conteudo(self):
        r = self.client.get(reverse('biblioteca_detalhe', args=[self.soc.pk]))
        self.assertContains(r, 'Conteudo do texto')

    def test_conteudo_nao_publicado_da_404(self):
        self.assertEqual(self.client.get(reverse('biblioteca_detalhe', args=[self.oculto.pk])).status_code, 404)

    def test_formatos_de_link_do_youtube(self):
        for link in ('https://youtu.be/dQw4w9WgXcQ', 'https://www.youtube.com/embed/dQw4w9WgXcQ', 'https://www.youtube.com/watch?feature=share&v=dQw4w9WgXcQ'):
            self.assertEqual(Conteudo(link_video=link).id_youtube, 'dQw4w9WgXcQ')

    def test_link_que_nao_e_do_youtube_e_rejeitado(self):
        with self.assertRaises(ValidationError):
            Conteudo(titulo='x', descricao='x', categoria='social', link_video='https://exemplo.com/video').clean()

    def test_menu_lateral_tem_biblioteca(self):
        r = self.client.get(reverse('biblioteca'))
        self.assertContains(r, 'ci-book-open')
        self.assertContains(r, 'aria-current="page"')


class ConteudosIniciaisTests(TestCase):
    def test_migration_cria_tutoriais_de_video_e_texto(self):
        self.assertGreaterEqual(Conteudo.objects.count(), 9)
        self.assertTrue(Conteudo.objects.filter(tipo='video').exists())
        self.assertTrue(Conteudo.objects.filter(tipo='texto').exists())
        for categoria, _ in Conteudo.CATEGORIAS:
            self.assertTrue(Conteudo.objects.filter(categoria=categoria).exists())

    def test_ha_um_video_para_cada_pilar(self):
        for pilar in ('Ambiental (E)', 'Social (S)', 'Governança (G)'):
            self.assertTrue(Conteudo.objects.filter(titulo__startswith=f'Pilar {pilar}', tipo='video').exists())

    def test_tutoriais_de_video_tem_texto_completo(self):
        for c in Conteudo.objects.filter(tipo='video'):
            self.assertGreaterEqual(len(c.texto.split()), 200, c.titulo)
