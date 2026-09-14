from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Empresa, PerfilUsuario


class RelatorioOperacionalTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(codigo='REL', nome='Relatórios')
        user = User.objects.create_user(username='gerente', password='senha')
        PerfilUsuario.objects.create(user=user, empresa=self.empresa, perfil='gerente')
        self.client.login(username='gerente', password='senha')

    def test_relatorio_de_veiculos_existe(self):
        response = self.client.get(reverse('relatorios:operacional', args=['veiculos']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Relatório de Veículos')
