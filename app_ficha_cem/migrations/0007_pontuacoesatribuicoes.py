# Generated by Django 4.1.3 on 2022-11-16 22:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_ficha_cem', '0006_alter_faltas_pessoas_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='PontuacoesAtribuicoes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ano', models.CharField(max_length=5)),
                ('cargo', models.CharField(max_length=5)),
                ('funcao', models.CharField(max_length=5)),
                ('ue', models.CharField(max_length=5)),
                ('pessoa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_ficha_cem.pessoas')),
            ],
            options={
                'unique_together': {('ano', 'pessoa')},
            },
        ),
    ]
