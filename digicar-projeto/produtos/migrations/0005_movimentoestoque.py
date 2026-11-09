from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('produtos', '0004_alter_produto_codigo')]

    operations = [
        migrations.CreateModel(
            name='MovimentoEstoque',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('entrada', 'Entrada'), ('saida', 'Saída'), ('ajuste', 'Ajuste')], max_length=10, verbose_name='Tipo')),
                ('quantidade', models.DecimalField(decimal_places=3, max_digits=12, verbose_name='Quantidade')),
                ('estoque_anterior', models.DecimalField(decimal_places=3, max_digits=12)),
                ('estoque_posterior', models.DecimalField(decimal_places=3, max_digits=12)),
                ('motivo', models.CharField(blank=True, max_length=255, verbose_name='Motivo')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movimentos', to='produtos.produto')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={'ordering': ['-criado_em'], 'verbose_name': 'Movimentação de estoque', 'verbose_name_plural': 'Movimentações de estoque'},
        ),
    ]
