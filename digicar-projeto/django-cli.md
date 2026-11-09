# Django CLI - Guia Completo de Comandos

Este documento reúne os comandos mais importantes do Django CLI para uso diário no projeto.

## 1) Como ver todos os comandos disponíveis

Para listar todos os comandos que existem no seu ambiente atual (incluindo apps instaladas e comandos customizados):

```bash
python manage.py help
```

Para listar apenas os nomes dos comandos:

```bash
python manage.py help --commands
```

Para ajuda de um comando específico:

```bash
python manage.py help <comando>
```

Exemplo:

```bash
python manage.py help migrate
```

---

## 2) Comandos principais (dia a dia)

### Desenvolvimento

```bash
python manage.py runserver
python manage.py runserver 0.0.0.0:8000
python manage.py runserver 127.0.0.1:9000
```

### Banco de dados e migrações

```bash
python manage.py makemigrations
python manage.py makemigrations <app>
python manage.py migrate
python manage.py migrate <app>
python manage.py showmigrations
python manage.py sqlmigrate <app> <migration_number>
python manage.py squashmigrations <app> <start_migration> <end_migration>
python manage.py optimizemigration <app> <migration_name>
```

### Shell e inspeção

```bash
python manage.py shell
python manage.py check
python manage.py check --deploy
python manage.py diffsettings
python manage.py inspectdb
python manage.py dbshell
```

### Administração de usuários

```bash
python manage.py createsuperuser
python manage.py changepassword <username>
```

### Dados (backup e carga)

```bash
python manage.py dumpdata > backup.json
python manage.py dumpdata <app.Model> --indent 2 > dados.json
python manage.py loaddata backup.json
```

### Testes

```bash
python manage.py test
python manage.py test <app>
python manage.py test <app.tests.TestClass>
```

---

## 3) Lista de comandos Django por categoria

Observação: alguns comandos só aparecem quando apps específicas estão instaladas no INSTALLED_APPS.

### Núcleo

- check
- compilemessages
- createcachetable
- dbshell
- diffsettings
- dumpdata
- flush
- inspectdb
- loaddata
- makemessages
- makemigrations
- migrate
- optimizemigration
- runserver
- sendtestemail
- shell
- showmigrations
- sqlflush
- sqlmigrate
- sqlsequencereset
- squashmigrations
- startapp
- startproject
- test
- testserver

### Autenticação (django.contrib.auth)

- changepassword
- createsuperuser

### Sessões (django.contrib.sessions)

- clearsessions

### Conteúdo (django.contrib.contenttypes)

- remove_stale_contenttypes

### Arquivos estáticos (django.contrib.staticfiles)

- collectstatic
- findstatic
- runserver (integrado no fluxo de staticfiles em desenvolvimento)

---

## 4) Comandos avançados e úteis

### Migrações detalhadas

```bash
# Criar migrações vazias para editar manualmente
python manage.py makemigrations --empty <app>

# Mostrar plano de migração
python manage.py migrate --plan

# Marcar como aplicada sem executar SQL
python manage.py migrate --fake

# Voltar para migração específica
python manage.py migrate <app> <migration_name>
```

### Performance e segurança

```bash
# Checagens completas para produção
python manage.py check --deploy

# Coletar arquivos estáticos para produção
python manage.py collectstatic --noinput
```

### Internacionalização

```bash
# Extrair traduções
python manage.py makemessages -l pt_BR

# Compilar traduções
python manage.py compilemessages
```

---

## 5) Fluxos recomendados

### Fluxo comum após alterar models.py

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### Fluxo para preparar produção

```bash
python manage.py check --deploy
python manage.py migrate
python manage.py collectstatic --noinput
```

### Fluxo para testes

```bash
python manage.py test
```

---

## 6) Comandos globais do django-admin

Além de usar manage.py, você pode usar django-admin para comandos globais:

```bash
django-admin --version
django-admin help
django-admin help --commands
django-admin startproject nome_projeto
django-admin startapp nome_app
```

No projeto, prefira manage.py porque ele já usa as configurações corretas (DJANGO_SETTINGS_MODULE).

---

## 7) Comandos específicos do seu projeto

Se você ou sua equipe criaram comandos customizados (management/commands), eles aparecerão em:

```bash
python manage.py help
python manage.py help --commands
```

Isso garante que você veja literalmente todos os comandos disponíveis no ambiente atual.
