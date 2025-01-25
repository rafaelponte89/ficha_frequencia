
from django.urls import path
from .views import cadastrar_pessoas,  pesquisar_pessoas, tela_pesquisar_pessoas, atualizar_pessoa

urlpatterns = [
    path('cadastrarpessoas', cadastrar_pessoas, name="cadastrarpessoas"),
    path('telapesquisar',tela_pesquisar_pessoas, name="telapesquisarpessoas"),
    path('pesquisar/',pesquisar_pessoas, name="pesquisarpessoas"),
    path('atualizarpessoa/<int:pessoa_id>', atualizar_pessoa, name="atualizarpessoa")
]