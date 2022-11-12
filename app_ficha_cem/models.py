from django.db import models

# Create your models here.

class Faltas(models.Model):
   
    tipo = models.CharField(max_length=3)
    descricao =  models.CharField(max_length=30)

    def __str__(self):
        return f'{self.tipo}'


class Pessoas(models.Model):
    # id = models.CharField(max_length=6, primary_key=True)
    nome = models.CharField(max_length=150)
    # admissao = models.DateField()

class Faltas_Pessoas(models.Model):
   
    data = models.DateField()
    pessoa = models.ForeignKey(Pessoas, on_delete=models.CASCADE)
    falta = models.ForeignKey(Faltas, on_delete=models.CASCADE)

    class Meta:
        unique_together=('pessoa','data')

# em desenvolvimento salvar pontuações
class Pontuacoes(models.Model):

    ano = models.CharField(max_length=5)
    cargo = models.CharField(max_length=5)
    funcao = models.CharField(max_length=5)
    ue = models.CharField(max_length=5)
    pessoa = models.ForeignKey(Pessoas, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('ano','pessoa')

   