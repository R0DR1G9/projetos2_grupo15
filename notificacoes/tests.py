from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from atividades.models import Atividade
from mensagens.models import Conversa, Mensagem
from rede_social.models import Comentario, Post

from .models import Notificacao
from .servicos import sincronizar_prazos


def novo_usuario(nome):
    return get_user_model().objects.create_user(nome, password='senha-forte-123', first_name=nome.title())


class ComentarioEMensagemTests(TestCase):
    def setUp(self):
        self.ana = novo_usuario('ana')
        self.bia = novo_usuario('bia')
        self.post = Post.objects.create(autor=self.ana, conteudo='Como reduzir agua?')

    def test_comentario_de_outra_empresa_avisa_o_autor(self):
        Comentario.objects.create(post=self.post, autor=self.bia, conteudo='Meca o hidrometro')
        n = Notificacao.objects.get(usuario=self.ana)
        self.assertEqual(n.tipo, 'comentario')
        self.assertIn('Bia comentou na sua publicação', n.texto)
        self.assertEqual(n.link, self.post.get_absolute_url())
        self.assertFalse(Notificacao.objects.filter(usuario=self.bia).exists())

    def test_comentar_na_propria_publicacao_nao_avisa(self):
        Comentario.objects.create(post=self.post, autor=self.ana, conteudo='Complemento')
        self.assertEqual(Notificacao.objects.count(), 0)

    def test_mensagem_avisa_o_destinatario(self):
        conversa = Conversa.entre(self.ana, self.bia, criar=True)
        Mensagem.objects.create(conversa=conversa, remetente=self.bia, texto='Oi!')
        n = Notificacao.objects.get(usuario=self.ana)
        self.assertEqual(n.tipo, 'mensagem')
        self.assertEqual(n.texto, 'Nova mensagem de Bia')
        self.assertEqual(n.link, reverse('mensagens:conversa', args=['bia']))

    def test_varias_mensagens_nao_lidas_geram_uma_notificacao(self):
        conversa = Conversa.entre(self.ana, self.bia, criar=True)
        for texto in ('Oi', 'Tudo bem?', 'Viu o post?'):
            Mensagem.objects.create(conversa=conversa, remetente=self.bia, texto=texto)
        self.assertEqual(Notificacao.objects.filter(usuario=self.ana).count(), 1)

    def test_depois_de_lida_uma_nova_mensagem_gera_outra(self):
        conversa = Conversa.entre(self.ana, self.bia, criar=True)
        Mensagem.objects.create(conversa=conversa, remetente=self.bia, texto='Oi')
        Notificacao.objects.update(lida=True)
        Mensagem.objects.create(conversa=conversa, remetente=self.bia, texto='De novo')
        self.assertEqual(Notificacao.objects.filter(usuario=self.ana).count(), 2)


class PrazoTests(TestCase):
    def setUp(self):
        self.user = novo_usuario('gestora')
        self.hoje = timezone.localdate()

    def atividade(self, dias, status='aguardando'):
        return Atividade.objects.create(usuario=self.user, titulo='Trocar lampadas', categoria='ambiental', status=status, prazo=self.hoje + timedelta(days=dias))

    def test_atrasada_gera_aviso(self):
        self.atividade(-2)
        sincronizar_prazos(self.user)
        n = Notificacao.objects.get()
        self.assertEqual(n.tipo, 'prazo')
        self.assertEqual(n.texto, 'Trocar lampadas - Atrasada há 2 dias')
        self.assertEqual(n.link, reverse('quadro_atividades'))

    def test_prazo_proximo_gera_aviso(self):
        self.atividade(2)
        sincronizar_prazos(self.user)
        self.assertEqual(Notificacao.objects.get().texto, 'Trocar lampadas - Vence em 2 dias')

    def test_prazo_distante_ou_concluida_nao_gera(self):
        self.atividade(10)
        self.atividade(-3, status='concluido')
        Atividade.objects.create(usuario=self.user, titulo='Sem prazo', categoria='social')
        sincronizar_prazos(self.user)
        self.assertEqual(Notificacao.objects.count(), 0)

    def test_sincronizar_varias_vezes_nao_duplica(self):
        self.atividade(-1)
        for _ in range(3):
            sincronizar_prazos(self.user)
        self.assertEqual(Notificacao.objects.count(), 1)

    def test_nao_avisa_sobre_atividade_de_outra_empresa(self):
        outra = novo_usuario('outra')
        Atividade.objects.create(usuario=outra, titulo='Dela', categoria='social', prazo=self.hoje - timedelta(days=1))
        sincronizar_prazos(self.user)
        self.assertEqual(Notificacao.objects.count(), 0)


class SinoETelaTests(TestCase):
    def setUp(self):
        self.user = novo_usuario('gestora')
        self.outra = novo_usuario('outra')
        self.client.force_login(self.user)
        self.n = Notificacao.objects.create(usuario=self.user, tipo='comentario', texto='Bia comentou na sua publicação', link='/social/')

    def test_sino_mostra_contagem_e_texto(self):
        resp = self.client.get(reverse('inicio'))
        self.assertContains(resp, 'data-sino-contagem')
        self.assertContains(resp, 'Bia comentou na sua publicação')

    def test_sino_gerado_por_prazo_na_hora_de_abrir_a_pagina(self):
        Atividade.objects.create(usuario=self.user, titulo='Auditar fornecedores', categoria='governanca', prazo=timezone.localdate() - timedelta(days=1))
        resp = self.client.get(reverse('inicio'))
        self.assertContains(resp, 'Auditar fornecedores - Atrasada há 1 dia')

    def test_abrir_marca_como_lida_e_redireciona(self):
        resp = self.client.get(reverse('notificacoes:abrir', args=[self.n.pk]))
        self.assertRedirects(resp, '/social/', fetch_redirect_response=False)
        self.n.refresh_from_db()
        self.assertTrue(self.n.lida)

    def test_marcar_todas_como_lidas(self):
        Notificacao.objects.create(usuario=self.user, tipo='prazo', texto='Outra')
        self.client.post(reverse('notificacoes:marcar_todas'))
        self.assertEqual(self.user.notificacoes.filter(lida=False).count(), 0)

    def test_nao_abre_notificacao_de_outra_empresa(self):
        alheia = Notificacao.objects.create(usuario=self.outra, tipo='prazo', texto='Segredo')
        self.assertEqual(self.client.get(reverse('notificacoes:abrir', args=[alheia.pk])).status_code, 404)
        self.assertNotContains(self.client.get(reverse('notificacoes:lista')), 'Segredo')

    def test_lista_exige_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse('notificacoes:lista')).status_code, 302)

    def test_lista_mostra_as_notificacoes(self):
        self.assertContains(self.client.get(reverse('notificacoes:lista')), 'Bia comentou na sua publicação')
