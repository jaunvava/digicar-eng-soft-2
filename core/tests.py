from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from clientes.models import Cliente
from .models import Empresa, PerfilUsuario


class PermissoesTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(codigo='PERM', nome='Permissões')
        self.operador = User.objects.create_user('operador', password='senha')
        PerfilUsuario.objects.create(user=self.operador, empresa=self.empresa, perfil='operador')
        self.cliente = Cliente.objects.create(empresa=self.empresa, nome='Cliente')
        self.client.login(username='operador', password='senha')

    def test_operador_nao_acessa_relatorios(self):
        self.assertEqual(self.client.get(reverse('relatorios:index')).status_code, 403)

    def test_operador_nao_exclui_por_rota_get(self):
        response = self.client.get(reverse('clientes:excluir', args=[self.cliente.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Cliente.objects.filter(pk=self.cliente.pk).exists())
