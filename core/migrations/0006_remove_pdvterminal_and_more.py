from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_empresa_apenas_digios_local_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='configuracaoempresa',
            name='ativar_impressao_pos_venda',
        ),
        migrations.DeleteModel(
            name='PdvTerminal',
        ),
    ]
