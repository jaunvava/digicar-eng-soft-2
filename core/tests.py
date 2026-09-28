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
from storage.local_adapter import LocalStorageAdapter
from storage.manager import StorageManager
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


class StorageManagerTests(SimpleTestCase):
    def setUp(self):
        # Apenas para isolar os testes; nao e uma API de reset da aplicacao.
        StorageManager._instance = None

    def tearDown(self):
        StorageManager._instance = None

    @patch("storage.manager.MongoStorageAdapter")
    def test_get_instance_retorna_sempre_o_mesmo_objeto(self, _):
        self.assertIs(StorageManager.get_instance(), StorageManager.get_instance())

    def test_construtor_direto_e_bloqueado(self):
        with self.assertRaises(TypeError):
            StorageManager()

    @override_settings(MONGO_URI="mongodb://mongo:27017", MONGO_DATABASE="arquivos")
    @patch("storage.manager.MongoStorageAdapter")
    def test_mongo_adapter_criado_uma_vez(self, adapter):
        StorageManager.get_instance()
        StorageManager.get_instance()

        adapter.assert_called_once_with(
            connection_string="mongodb://mongo:27017",
            database_name="arquivos",
        )

    @patch("storage.manager.MongoStorageAdapter")
    def test_service_recebe_adapter_do_manager(self, _):
        manager = StorageManager.get_instance()
        service = ArquivoService(manager.get_local_adapter())

        self.assertIs(service.storage, manager.get_local_adapter())

    @patch("storage.manager.MongoStorageAdapter")
    def test_adapter_configurado_segue_file_storage(self, _):
        manager = StorageManager.get_instance()

        with override_settings(FILE_STORAGE="local"):
            self.assertIs(manager.get_adapter_configurado(), manager.get_local_adapter())
        with override_settings(FILE_STORAGE="mongo"):
            self.assertIs(manager.get_adapter_configurado(), manager.get_mongo_adapter())
        with override_settings(FILE_STORAGE="outro"):
            with self.assertRaises(ValueError):
                manager.get_adapter_configurado()


class ArquivoStorageTests(SimpleTestCase):

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