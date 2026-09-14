from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('clientes', '0001_initial')]

    operations = [
        migrations.CreateModel(
            name='Veiculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('placa', models.CharField(max_length=10, verbose_name='Placa')),
                ('marca', models.CharField(blank=True, max_length=100, verbose_name='Marca')),
                ('modelo', models.CharField(max_length=100, verbose_name='Modelo')),
                ('ano', models.PositiveIntegerField(blank=True, null=True, verbose_name='Ano')),
                ('cor', models.CharField(blank=True, max_length=50, verbose_name='Cor')),
                ('chassi', models.CharField(blank=True, max_length=30, verbose_name='Chassi')),
                ('observacoes', models.TextField(blank=True, verbose_name='Observações')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='veiculos', to='clientes.cliente')),
            ],
            options={'ordering': ['placa'], 'verbose_name': 'Veículo', 'verbose_name_plural': 'Veículos'},
        ),
        migrations.AddConstraint(
            model_name='veiculo',
            constraint=models.UniqueConstraint(fields=('cliente', 'placa'), name='veiculo_placa_por_cliente'),
        ),
    ]
