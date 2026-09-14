from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('clientes', '0002_veiculo'), ('ordens', '0001_initial')]

    operations = [
        migrations.AddField(
            model_name='ordemservico', name='veiculo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordens_servico', to='clientes.veiculo'),
        ),
    ]
