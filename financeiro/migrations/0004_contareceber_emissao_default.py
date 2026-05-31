import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0003_baixacontapagar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contareceber',
            name='emissao',
            field=models.DateField(default=datetime.date.today, verbose_name='Data Emissão'),
        ),
    ]
