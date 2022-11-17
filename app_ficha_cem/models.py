from django.db import models
from django.utils.timezone import now
# Create your models here.

# licença nojo 8 dias corridos
# licença paternidade 5 dias úteis

class Faltas(models.Model):
   
    tipo = models.CharField(max_length=3)
    descricao =  models.CharField(max_length=30)
    
    def __str__(self):
        return f'{self.descricao}'


class Pessoas(models.Model):
    # id = models.CharField(max_length=6, primary_key=True)
    nome = models.CharField(max_length=150)
    admissao = models.DateField(default='1991-01-01')

class Faltas_Pessoas(models.Model):
    
    pessoa = models.ForeignKey(Pessoas, on_delete=models.CASCADE)
    data = models.DateField(default=now )
    falta = models.ForeignKey(Faltas, on_delete=models.CASCADE)
    qtd_dias = models.IntegerField(default=1)

    class Meta:
        unique_together=('pessoa','data')

    def __str__(self):
        return f'{self.pessoa}, {self.falta.tipo}, {self.data}'

# em desenvolvimento salvar pontuações
class Pontuacoes(models.Model):

    ano = models.CharField(max_length=5)
    cargo = models.CharField(max_length=5)
    funcao = models.CharField(max_length=5)
    ue = models.CharField(max_length=5)
    pessoa = models.ForeignKey(Pessoas, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('ano','pessoa')

class PontuacoesAtribuicoes(models.Model):

    ano = models.CharField(max_length=5)
    cargo = models.CharField(max_length=5)
    funcao = models.CharField(max_length=5)
    ue = models.CharField(max_length=5)
    pessoa = models.ForeignKey(Pessoas, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('ano','pessoa')

   