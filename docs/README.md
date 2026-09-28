# Padrões de projeto no app `storage`

O app `storage` guarda os arquivos enviados pelo sistema (imagens e documentos dos `ImageField`/`FileField`), no sistema de arquivos local ou no MongoDB (GridFS). Ele segue a mesma estrutura da referência de sala, que combina **Singleton** e **Adapter**.

| Documento | Conteúdo |
|---|---|
| [singleton-storage.md](singleton-storage.md) | `StorageManager`: instância única que guarda os adapters |
| [adapter-storage.md](adapter-storage.md) | `ArquivoStorage` e seus adapters para disco local e GridFS |

> A referência (`docs/ref/*.java`) fica apenas na máquina local e está no `.gitignore`. Os trechos necessários foram copiados nos documentos acima.

## Como os dois padrões se encaixam

| Papel | Referência (Java) | Projeto (Python) |
|---|---|---|
| Singleton | `DatabaseManager` | `StorageManager` ([`storage/manager.py`](../storage/manager.py)) |
| Target do Adapter | `DataBaseAdapter` | `ArquivoStorage` ([`storage/interfaces.py`](../storage/interfaces.py)) |
| Adapters | `PostgresAdapter`, `MongoAdapter` | `LocalStorageAdapter`, `MongoStorageAdapter` |
| Adaptees | `PostgresClient`, `MongoClient` | `pathlib.Path` (disco), `pymongo.MongoClient` + `GridFS` |
| Cliente | `UsuarioService` | `ArquivoService` ([`storage/service.py`](../storage/service.py)) |
| Quem usa o cliente | `Main` | `MongoGridFSStorage`, `servir_gridfs` |

```mermaid
classDiagram
    class StorageManager {
        <<Singleton>>
        +get_instance()$
        +get_local_adapter()
        +get_mongo_adapter()
        +get_adapter_configurado()
    }
    class ArquivoStorage {
        <<Target>>
        +conectar()
        +desconectar()
        +salvar() +buscar() +excluir() +existe()
    }
    class LocalStorageAdapter {
        <<Adapter>>
    }
    class MongoStorageAdapter {
        <<Adapter>>
    }
    class ArquivoService {
        <<Cliente>>
    }
    StorageManager o-- LocalStorageAdapter
    StorageManager o-- MongoStorageAdapter
    LocalStorageAdapter ..|> ArquivoStorage
    MongoStorageAdapter ..|> ArquivoStorage
    LocalStorageAdapter --> Path : adapta
    MongoStorageAdapter --> GridFS : adapta
    ArquivoService --> ArquivoStorage
    MongoGridFSStorage --> ArquivoService
    servir_gridfs --> ArquivoService
```

## Fluxo de uma requisição

Exemplo: o navegador pede uma imagem salva no GridFS (`GET /media/gridfs/<id>`, com `FILE_STORAGE=mongo`).

```mermaid
sequenceDiagram
    participant V as servir_gridfs
    participant M as StorageManager
    participant S as ArquivoService
    participant A as MongoStorageAdapter
    participant G as MongoClient / GridFS

    V->>M: get_instance()
    Note over M: 1ª chamada cria MongoClient e adapters,<br/>as seguintes devolvem a mesma instância
    M-->>V: manager
    V->>M: get_mongo_adapter()
    M-->>V: adapter
    V->>S: ArquivoService(adapter).buscar(id)
    S->>A: conectar()
    A->>G: admin.command("ping")
    S->>A: buscar(id)
    A->>G: fs.get(ObjectId(id))
    G-->>A: arquivo
    A-->>S: bytes
    S->>A: desconectar()
    S-->>V: bytes
```

O equivalente em Python do `Main.java`:

```python
from storage.manager import StorageManager
from storage.service import ArquivoService

manager = StorageManager.get_instance()

arquivos_locais = ArquivoService(manager.get_local_adapter())
arquivos_mongo  = ArquivoService(manager.get_mongo_adapter())

arquivos_locais.salvar("documentos/contrato.pdf", conteudo)
arquivos_mongo.salvar("documentos/contrato.pdf", conteudo)
```

## Configuração

Definida em [`digicar/settings.py`](../digicar/settings.py) por variáveis de ambiente:

| Variável | Padrão | Uso |
|---|---|---|
| `FILE_STORAGE` | `local` | `local` usa o `FileSystemStorage` do Django; `mongo` troca o backend padrão para `MongoGridFSStorage`. Também define o retorno de `get_adapter_configurado()` |
| `MONGO_URI` | `mongodb://localhost:27017` | URI do `MongoClient` criado pelo `StorageManager` |
| `MONGO_DATABASE` | `digicar` | banco usado pelo GridFS |
| `MEDIA_ROOT` | `<projeto>/media` | diretório base do `LocalStorageAdapter` |

O `StorageManager` lê essas configurações **uma única vez**, na primeira chamada de `get_instance()`. Depois de alterá-las, reinicie a aplicação.

## Testes

```bash
python manage.py test core
```

Os testes do storage ficam em [`core/tests.py`](../core/tests.py): `StorageManagerTests`, `ArquivoServiceTests`, `ArquivoStorageTests` e `MongoStorageAdapterTests`. O Mongo é simulado com *mocks*, então não é preciso ter um MongoDB rodando.
