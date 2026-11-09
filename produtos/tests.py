from decimal import Decimal
from io import BytesIO
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image
from core.models import Empresa, PerfilUsuario
from .models import Produto, MovimentoEstoque


class EstoqueTests(TestCase):
    def setUp(self):
        empresa = Empresa.objects.create(codigo='EST', nome='Estoque Teste')
        self.produto = Produto.objects.create(empresa=empresa, nome='Pastilha', tipo='produto', estoque_atual=10)

    def test_movimentacao_registra_saldo_anterior_e_posterior(self):
        movimento = MovimentoEstoque.objects.create(produto=self.produto, tipo='entrada', quantidade=5,
            estoque_anterior=10, estoque_posterior=15, motivo='Compra')
        self.assertEqual(movimento.estoque_posterior, Decimal('15'))


@override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.InMemoryStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})
class ImagemProdutoTests(TestCase):
    def setUp(self):
        empresa = Empresa.objects.create(codigo='IMG', nome='Imagem Teste')
        user = User.objects.create_user('gerente', password='senha123')
        PerfilUsuario.objects.create(user=user, empresa=empresa, perfil='admin')
        self.client.force_login(user)
        self.produto = Produto.objects.create(empresa=empresa, nome='Filtro', preco_venda=10)

    def _png(self, nome='foto.png'):
        buffer = BytesIO()
        Image.new('RGB', (2, 2), 'red').save(buffer, 'PNG')
        return SimpleUploadedFile(nome, buffer.getvalue(), content_type='image/png')

    def _dados(self, **extra):
        return {'nome': 'Filtro', 'tipo': 'produto', 'preco_venda': '10', 'estoque_atual': '0', **extra}

    def test_upload_grava_imagem_com_id_do_produto_e_renderiza(self):
        self.client.post(reverse('produtos:editar', args=[self.produto.pk]), self._dados(imagem=self._png()))
        self.produto.refresh_from_db()
        self.assertTrue(self.produto.imagem.name.startswith(f'produtos/{self.produto.pk}/'))
        resposta = self.client.get(reverse('produtos:editar', args=[self.produto.pk]))
        self.assertContains(resposta, f'src="{self.produto.imagem.url}"')

    def test_troca_apaga_imagem_antiga(self):
        url = reverse('produtos:editar', args=[self.produto.pk])
        self.client.post(url, self._dados(imagem=self._png('a.png')))
        self.produto.refresh_from_db()
        antiga = self.produto.imagem.name
        self.client.post(url, self._dados(imagem=self._png('b.png')))
        self.produto.refresh_from_db()
        self.assertNotEqual(self.produto.imagem.name, antiga)
        self.assertFalse(self.produto.imagem.storage.exists(antiga))

    def test_arquivo_que_nao_e_imagem_nao_cria_produto(self):
        falso = SimpleUploadedFile('x.png', b'nao sou imagem', content_type='image/png')
        self.client.post(reverse('produtos:novo'), self._dados(nome='Novo', imagem=falso))
        self.assertFalse(Produto.objects.filter(nome='Novo').exists())

    def test_novo_com_imagem_cria_produto(self):
        resposta = self.client.post(reverse('produtos:novo'), self._dados(nome='Novo', imagem=self._png()))
        self.assertRedirects(resposta, reverse('produtos:lista'), fetch_redirect_response=False)
        novo = Produto.objects.get(nome='Novo')
        self.assertEqual(novo.imagem.name.split('/')[:2], ['produtos', str(novo.pk)])
