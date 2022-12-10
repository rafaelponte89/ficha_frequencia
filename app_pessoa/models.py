from django.db import models
from app_cargo.models import Cargos
# Create your models here.
class Pessoas(models.Model):
    EFETIVO =  (
     (True,'Sim'),
     (False,'Não')
    )
    id = models.CharField(max_length=6, primary_key=True)
    nome = models.CharField(max_length=150)
    dt_nasc = models.DateField(default='1991-01-01')
    cpf = models.CharField(max_length=11, default='11111111111')
    admissao = models.DateField(default='1991-01-01')
    efetivo = models.BooleanField(choices=EFETIVO, default=False)
    cargo = models.ForeignKey(Cargos, on_delete=models.CASCADE, related_name="pessoas_cargos")
