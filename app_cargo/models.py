from django.db import models

# Create your models here.

class Cargos(models.Model):
    cargo = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.cargo}'