# Generated by Django 5.1.1 on 2024-11-03 22:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_avaliacao_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comentario',
            name='receita',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.receita'),
        ),
    ]