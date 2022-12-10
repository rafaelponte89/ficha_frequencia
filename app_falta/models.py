from django.db import models

# Create your models here.
class Faltas(models.Model):
   
    tipo = models.CharField(max_length=3)
    descricao =  models.CharField(max_length=30)
    
    def __str__(self):
        return f'{self.descricao}'