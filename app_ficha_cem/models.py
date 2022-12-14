from django.db import models
from django.utils.timezone import now
from app_falta.models import Faltas
from app_pessoa.models import Pessoas
from app_cargo.models import Cargos

# Create your models here.

# licença nojo 8 dias corridos
# licença paternidade 5 dias úteis
class Faltas_Pessoas(models.Model):
    
    pessoa = models.ForeignKey(Pessoas, on_delete=models.CASCADE)
    data = models.DateField(default=now)
    falta = models.ForeignKey(Faltas, on_delete=models.CASCADE)
    qtd_dias = models.IntegerField(default=1)

    class Meta:
        unique_together=('pessoa','data')

    def __str__(self):
        return f'{self.pessoa}, {self.falta.tipo}, {self.data}'

# em desenvolvimento salvar pontuações
class Pontuacoes(models.Model):

    ano = models.IntegerField()
    cargo = models.IntegerField()
    funcao = models.IntegerField()
    ue = models.IntegerField()

    cargo_atrib = models.IntegerField()
    funcao_atrib = models.IntegerField()
    ue_atrib = models.IntegerField() 

    pessoa = models.ForeignKey(Pessoas, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('ano','pessoa')

    def __str__(self):
        return self.ano



   