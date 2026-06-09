# Migra o BannerDashboard de armazenamento em arquivo (media/banners/) para BLOB no banco de dados
import mimetypes
import os

from django.conf import settings
from django.db import migrations, models


def migrar_imagens_para_db(apps, schema_editor):
    BannerDashboard = apps.get_model('core', 'BannerDashboard')
    for banner in BannerDashboard.objects.all():
        caminho_relativo = banner.imagem_antiga or ''
        dados = b''
        tipo = 'image/jpeg'
        nome = os.path.basename(caminho_relativo) if caminho_relativo else ''

        if caminho_relativo:
            caminho_absoluto = os.path.join(settings.MEDIA_ROOT, caminho_relativo)
            if os.path.isfile(caminho_absoluto):
                with open(caminho_absoluto, 'rb') as f:
                    dados = f.read()
                tipo_detectado, _ = mimetypes.guess_type(caminho_absoluto)
                if tipo_detectado:
                    tipo = tipo_detectado

        banner.imagem_dados = dados
        banner.imagem_tipo = tipo
        banner.imagem_nome = nome
        banner.save(update_fields=['imagem_dados', 'imagem_tipo', 'imagem_nome'])


def reverter_migracao(apps, schema_editor):
    # Não há como reconstruir os arquivos originais; nada a fazer.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_remove_empresa_apenas_digios_local'),
    ]

    operations = [
        # 1) Renomeia o campo antigo (ImageField) para preservar os caminhos durante a migração de dados
        migrations.RenameField(
            model_name='bannerdashboard',
            old_name='imagem',
            new_name='imagem_antiga',
        ),
        migrations.AlterField(
            model_name='bannerdashboard',
            name='imagem_antiga',
            field=models.CharField(max_length=255, blank=True, null=True),
        ),

        # 2) Novos campos para armazenar a imagem como binário no banco
        migrations.AddField(
            model_name='bannerdashboard',
            name='imagem_dados',
            field=models.BinaryField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bannerdashboard',
            name='imagem_tipo',
            field=models.CharField(max_length=100, default='image/jpeg', verbose_name='Tipo do Arquivo'),
        ),
        migrations.AddField(
            model_name='bannerdashboard',
            name='imagem_nome',
            field=models.CharField(max_length=255, blank=True, verbose_name='Nome do Arquivo'),
        ),

        # 3) Lê os arquivos de media/banners/ e copia o conteúdo para o banco
        migrations.RunPython(migrar_imagens_para_db, reverter_migracao),

        # 4) Remove o campo antigo baseado em arquivo e promove o novo campo binário para "imagem"
        migrations.RemoveField(
            model_name='bannerdashboard',
            name='imagem_antiga',
        ),
        migrations.RenameField(
            model_name='bannerdashboard',
            old_name='imagem_dados',
            new_name='imagem',
        ),
        migrations.AlterField(
            model_name='bannerdashboard',
            name='imagem',
            field=models.BinaryField(
                default=b'',
                verbose_name='Imagem',
                help_text='Tamanho recomendado para a imagem: 1200x320 pixels (ou proporção equivalente).',
            ),
            preserve_default=False,
        ),
    ]
