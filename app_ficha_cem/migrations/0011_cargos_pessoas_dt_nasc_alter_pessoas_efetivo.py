# Generated by Django 4.1.3 on 2022-11-25 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_ficha_cem', '0010_pessoas_efetivo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cargos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cargo', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='pessoas',
            name='dt_nasc',
            field=models.DateField(default='1991-01-01'),
        ),
        migrations.AlterField(
            model_name='pessoas',
            name='efetivo',
            field=models.BooleanField(choices=[(True, 'Sim'), (False, 'Não')], default=False, verbose_name='Efetivo: '),
        ),
    ]