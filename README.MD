# DigiCAR — Sistema de Gestão de Oficina

> Sistema web multi-tenant para gestão de Ordens de Serviço, controle financeiro, vendas e muito mais.  
> Construído com **Django 5** + **Bootstrap 5** + **SQLite**.

---

## 📦 Módulos

| Módulo                   | Funcionalidades                                                         |
| ------------------------ | ----------------------------------------------------------------------- |
| 🏠 **Dashboard**         | Indicadores em tempo real, gráficos de vendas e recebimentos (Chart.js) |
| 👥 **Clientes**          | Cadastro PF/PJ com veículos vinculados e histórico de serviços           |
| 📦 **Produtos**          | Entradas, saídas, ajustes e baixa automática de peças utilizadas nas OS   |
| 💰 **Financeiro**        | Contas a receber, contas a pagar, baixas parciais e totais              |
| 📄 **Orçamentos**        | Emissão e acompanhamento de orçamentos com fluxo de aprovação           |
| 🔧 **Ordens de Serviço** | OS completa com equipamento, peças, serviços, técnico e garantia        |
| 📊 **Relatórios**        | Clientes, veículos, estoque, ordens de serviço e financeiro              |

---

## 🏗️ Arquitetura

- **Multi-tenant**: cada empresa tem seus dados isolados por FK. SQLite, MySQL e PostgreSQL podem ser configurados simultaneamente.
- **Autenticação customizada**: login com Código da Empresa + Usuário + Senha.
- **Django MVT** com apps separados por domínio de negócio.
- **Veículos** ficam vinculados a clientes; cada veículo possui seu histórico de OS.
- **Estoque** mantém o saldo e o histórico de cada movimentação (entrada, saída e ajuste).
- Peças vinculadas a uma OS geram baixa automática; a exclusão da OS gera o estorno correspondente.
- **Permissões**: administrador gerencia tudo; gerente gerencia cadastros e operação; operador consulta e trabalha nas OS, sem excluir ou alterar cadastros protegidos.

---

## ⚙️ Requisitos

- Python 3.10+
- pip

---

## 🚀 Instalação

```bash
# 1. Clone o repositório
git clone <url-do-repo>
cd av3-eng

# 2. Crie e ative o ambiente virtual
python -m venv venv

# Windows
venv/Scripts/activate

# Linux/Mac
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute as migrações
python manage.py migrate

# 5. Crie a empresa e usuário inicial
# 5. Inicie o servidor
python manage.py runserver
```
Acesse: **http://127.0.0.1:8000/**

---

## 📁 Estrutura do Projeto

```
estoque/
├── core/               # Tenant, login, dashboard, middleware
├── clientes/           # Cadastro de clientes
├── produtos/           # Produtos, serviços, estoque
├── financeiro/         # Contas a receber/pagar, baixas
├── orcamentos/         # Orçamentos
├── ordens/             # Ordens de Serviço
├── templates/          # Templates HTML (Bootstrap 5)
├── static/             # CSS, JS, imagens
│   ├── css/app.css
│   └── js/app.js
├── digicar/            # Configurações do projeto Django
│   ├── settings.py
│   └── urls.py
├── manage.py
└── db.sqlite3          # Banco de dados local (não versionado)
```

---

## 🛠️ Tecnologias

- [Django 5](https://www.djangoproject.com/)
- [Bootstrap 5](https://getbootstrap.com/)
- [Bootstrap Icons](https://icons.getbootstrap.com/)
- [Chart.js](https://www.chartjs.org/)
- [ViaCEP](https://viacep.com.br/) (busca de CEP)
- SQLite (desenvolvimento)

### Bancos relacionais e arquivos

O banco `default` continua configurado pelas variáveis legadas `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` e `DB_PORT`. É possível adicionar até três aliases relacionais, `db2`, `db3` e `db4`, usando os mesmos sufixos numerados. Por exemplo:

```env
DB_ENGINE=postgresql
DB_NAME=digicar
DB_HOST=postgres-principal
DB_2_ENGINE=mysql
DB_2_NAME=relatorios
DB_2_HOST=mysql-relatorios
DB_2_USER=digicar
DB_2_PASSWORD=...
DB_3_ENGINE=sqlite
DB_3_NAME=/dados/legado.sqlite3
DB_APP_ROUTES=relatorios:db2,fornecedores:db3
```

Sem `DB_APP_ROUTES`, os apps Django continuam no `default`. Cada app roteado deve manter suas relações no mesmo banco; o roteador bloqueia migrações dos apps roteados nos demais aliases. Rode `python manage.py migrate --database=db2` para aplicar as migrações no alias configurado.

Uploads usam filesystem local por padrão (`FILE_STORAGE=local`). Com `FILE_STORAGE=mongo`, `MONGO_URI` e `MONGO_DATABASE` configuram o MongoDB/GridFS, e os `ImageField`/`FileField` Django passam a gravar e servir arquivos pelo GridFS.

---

## 📝 Adicionar nova empresa (multi-tenant)

```python
# No shell do Django
python manage.py shell

from core.models import Empresa, PerfilUsuario
from django.contrib.auth.models import User

# Cria empresa
empresa = Empresa.objects.create(codigo='EMP002', nome='Minha Empresa')

# Cria usuário vinculado
user = User.objects.create_user('operador', password='senha123')
PerfilUsuario.objects.create(user=user, empresa=empresa, perfil='operador')
```

---

## 📄 Licença

Uso interno. Todos os direitos reservados.

## ✅ Verificação

```bash
python3 manage.py check
python3 manage.py makemigrations --check --dry-run
python3 manage.py test
```
