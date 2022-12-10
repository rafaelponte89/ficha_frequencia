
from django.urls import path
from .views import pessoas, atualizar_pessoa

urlpatterns = [
    path('', pessoas, name="listarpessoas"),
    path('<str:pessoa_id>', atualizar_pessoa, name="atualizarpessoa"),
]