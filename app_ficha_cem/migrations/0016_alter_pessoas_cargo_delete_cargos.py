# Generated by Django 4.1.3 on 2022-12-08 23:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_cargo', '0001_initial'),
        ('app_ficha_cem', '0015_alter_pessoas_cargo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pessoas',
            name='cargo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pessoas_cargos', to='app_cargo.cargos'),
        ),
        migrations.DeleteModel(
            name='Cargos',
        ),
    ]
