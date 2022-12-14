# Generated by Django 4.1.3 on 2022-12-09 00:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_ficha_cem', '0018_remove_pessoas_cargo'),
        ('app_pessoa', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faltas_pessoas',
            name='pessoa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_pessoa.pessoas'),
        ),
        migrations.AlterField(
            model_name='pontuacoes',
            name='pessoa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_pessoa.pessoas'),
        ),
        migrations.AlterField(
            model_name='pontuacoesatribuicoes',
            name='pessoa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_pessoa.pessoas'),
        ),
        migrations.DeleteModel(
            name='Pessoas',
        ),
    ]
