# Generated by Django 4.1.3 on 2022-11-15 15:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app_ficha_cem', '0005_pessoas_admissao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faltas_pessoas',
            name='data',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
