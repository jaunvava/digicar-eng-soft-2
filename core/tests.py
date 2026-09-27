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
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from digicar.database import criar_configuracao_bancos
from storage.factory import criar_storage
from storage.local_adapter import LocalStorageAdapter
from storage.service import ArquivoService


class ConfiguracaoBancoTests(SimpleTestCase):
    def test_sqlite_e_padrao_sem_host(self):
        bancos = criar_configuracao_bancos({}, Path("/app"))

        self.assertEqual(bancos["default"]["ENGINE"], "django.db.backends.sqlite3")

    def test_mysql_mantem_compatibilidade_com_db_host(self):
        bancos = criar_configuracao_bancos({"DB_HOST": "db"}, Path("/app"))

        self.assertEqual(bancos["default"]["ENGINE"], "django.db.backends.mysql")
        self.assertEqual(bancos["default"]["PORT"], "3306")

    def test_postgresql_pode_ser_selecionado(self):
        bancos = criar_configuracao_bancos({"DB_ENGINE": "postgresql"}, Path("/app"))

        self.assertEqual(
            bancos["default"]["ENGINE"], "django.db.backends.postgresql"
        )
        self.assertEqual(bancos["default"]["PORT"], "5432")

    def test_engine_desconhecido_e_rejeitado(self):
        with self.assertRaisesMessage(ValueError, "DB_ENGINE inválido"):
            criar_configuracao_bancos({"DB_ENGINE": "desconhecido"}, Path("/app"))


class ArquivoStorageTests(SimpleTestCase):
    def tearDown(self):
        criar_storage.cache_clear()

    @override_settings(FILE_STORAGE="local")
    def test_factory_reutiliza_instancia_singleton(self):
        criar_storage.cache_clear()

        self.assertIs(criar_storage(), criar_storage())
        self.assertIs(ArquivoService().storage, ArquivoService().storage)

    @override_settings(
        FILE_STORAGE="mongo",
        MONGO_URI="mongodb://mongo:27017",
        MONGO_DATABASE="arquivos",
    )
    @patch("storage.factory.MongoStorageAdapter")
    def test_factory_configura_mongo_e_reutiliza_adapter(self, adapter):
        criar_storage.cache_clear()

        primeiro = criar_storage()
        segundo = criar_storage()

        self.assertIs(primeiro, segundo)
        adapter.assert_called_once_with(
            connection_string="mongodb://mongo:27017",
            database_name="arquivos",
        )

    def test_adapter_local_salva_busca_e_exclui(self):
        with TemporaryDirectory() as diretorio:
            with override_settings(MEDIA_ROOT=diretorio):
                storage = LocalStorageAdapter()
                identificador = storage.salvar("documentos/teste.txt", b"conteudo")

                self.assertEqual(storage.buscar(identificador), b"conteudo")
                self.assertTrue(storage.existe(identificador))
                storage.excluir(identificador)
                self.assertFalse(storage.existe(identificador))

    def test_adapter_local_bloqueia_caminho_fora_da_media(self):
        with TemporaryDirectory() as diretorio:
            with override_settings(MEDIA_ROOT=diretorio):
                with self.assertRaises(ValueError):
                    LocalStorageAdapter().salvar("../arquivo.txt", b"conteudo")