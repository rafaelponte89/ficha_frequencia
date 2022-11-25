from .views import gerar_ficha, faltas, atualizar_pessoa, \
      listar_ficha, encerrar_ano, pessoas, pessoas_faltas, pdf, imprimir, cargos
from django.urls.conf import path
urlpatterns = [
    path('pessoas/', pessoas, name="listarpessoas"),
    path('pessoas/<str:pessoa_id>', atualizar_pessoa, name="atualizarpessoa"),
    path('pessoas/<str:pessoa_id>/faltas', pessoas_faltas, name="lancarfalta" ),
    path('pessoas/<str:pessoa_id>/fichas', listar_ficha, name='listarficha' ),
    path('pessoas/<str:pessoa_id>/fichas/<int:ano>', gerar_ficha, name='ficha'),
    path('faltas/', faltas, name="listarfaltas"),
    path('pessoas/<str:pessoa_id>/fichas/encerramento/<int:ano>', encerrar_ano, name='encerrarano' ),
    path('cargos/', cargos, name='listarcargos'),
    path('pessoas/<int:pessoa_id>/fichas/<int:ano>/', pdf, name='imprimir'),
   
]