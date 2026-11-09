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
from unittest.mock import MagicMock, patch

from bson import ObjectId
from gridfs.errors import NoFile

from django.test import SimpleTestCase, override_settings

from digicar.database import criar_configuracao_bancos
from storage.interfaces import ArquivoStorage
from storage.local_adapter import LocalStorageAdapter
from storage.manager import StorageManager
from storage.mongo_adapter import MongoStorageAdapter
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
    @patch("storage.manager.MongoClient")
    def test_manager_cria_client_e_injeta_no_adapter_uma_vez(self, client, adapter):
        StorageManager.get_instance()
        StorageManager.get_instance()

        client.assert_called_once_with("mongodb://mongo:27017")
        adapter.assert_called_once_with(client.return_value, database_name="arquivos")

    @patch("storage.manager.MongoStorageAdapter")
    def test_manager_injeta_media_root_no_adapter_local(self, _):
        with TemporaryDirectory() as diretorio:
            with override_settings(MEDIA_ROOT=diretorio):
                adapter = StorageManager.get_instance().get_local_adapter()

                self.assertEqual(adapter.base_path, Path(diretorio).resolve())

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


class AdapterFalso(ArquivoStorage):
    def __init__(self):
        self.chamadas = []

    def conectar(self):
        self.chamadas.append("conectar")

    def desconectar(self):
        self.chamadas.append("desconectar")

    def salvar(self, nome, conteudo):
        self.chamadas.append("salvar")
        return nome

    def buscar(self, identificador):
        self.chamadas.append("buscar")
        raise FileNotFoundError(identificador)

    def excluir(self, identificador):
        self.chamadas.append("excluir")

    def existe(self, identificador):
        self.chamadas.append("existe")
        return True


class ArquivoServiceTests(SimpleTestCase):
    def test_service_conecta_e_desconecta_em_volta_da_operacao(self):
        adapter = AdapterFalso()

        self.assertEqual(ArquivoService(adapter).salvar("a.txt", b"x"), "a.txt")
        self.assertEqual(adapter.chamadas, ["conectar", "salvar", "desconectar"])

    def test_service_desconecta_mesmo_com_erro(self):
        adapter = AdapterFalso()

        with self.assertRaises(FileNotFoundError):
            ArquivoService(adapter).buscar("inexistente")
        self.assertEqual(adapter.chamadas, ["conectar", "buscar", "desconectar"])


class ArquivoStorageTests(SimpleTestCase):

    def test_adapter_local_salva_busca_e_exclui(self):
        with TemporaryDirectory() as diretorio:
            storage = LocalStorageAdapter(diretorio)
            identificador = storage.salvar("documentos/teste.txt", b"conteudo")

            self.assertEqual(storage.buscar(identificador), b"conteudo")
            self.assertTrue(storage.existe(identificador))
            storage.excluir(identificador)
            self.assertFalse(storage.existe(identificador))

    def test_adapter_local_bloqueia_caminho_fora_da_media(self):
        with TemporaryDirectory() as diretorio:
            with self.assertRaises(ValueError):
                LocalStorageAdapter(diretorio).salvar("../arquivo.txt", b"conteudo")

    def test_adapter_local_conectar_cria_diretorio_base(self):
        with TemporaryDirectory() as diretorio:
            base = Path(diretorio) / "media"
            LocalStorageAdapter(base).conectar()

            self.assertTrue(base.is_dir())


@patch("storage.mongo_adapter.GridFS")
class MongoStorageAdapterTests(SimpleTestCase):
    def test_adapter_usa_client_injetado(self, gridfs):
        client = MagicMock()
        adapter = MongoStorageAdapter(client, database_name="arquivos")

        self.assertIs(adapter.client, client)
        client.__getitem__.assert_called_once_with("arquivos")
        gridfs.assert_called_once_with(client.__getitem__.return_value)

    def test_conectar_verifica_conexao_com_ping(self, _):
        client = MagicMock()

        MongoStorageAdapter(client).conectar()

        client.admin.command.assert_called_once_with("ping")

    def test_desconectar_nao_fecha_client_compartilhado(self, _):
        client = MagicMock()

        MongoStorageAdapter(client).desconectar()

        client.close.assert_not_called()

    def test_salvar_traduz_para_gridfs_put(self, gridfs):
        arquivo_id = ObjectId()
        gridfs.return_value.put.return_value = arquivo_id

        identificador = MongoStorageAdapter(MagicMock()).salvar("foto.png", b"img")

        self.assertEqual(identificador, str(arquivo_id))
        self.assertEqual(gridfs.return_value.put.call_args.kwargs, {"filename": "foto.png"})

    def test_buscar_traduz_erros_para_file_not_found(self, gridfs):
        gridfs.return_value.get.side_effect = NoFile
        adapter = MongoStorageAdapter(MagicMock())

        with self.assertRaises(FileNotFoundError):
            adapter.buscar("id-invalido")
        with self.assertRaises(FileNotFoundError):
            adapter.buscar(str(ObjectId()))

    def test_excluir_id_invalido_nao_falha(self, gridfs):
        MongoStorageAdapter(MagicMock()).excluir("id-invalido")

        gridfs.return_value.delete.assert_not_called()
