from .views import gerar_ficha, faltas, atualizar_pessoa, \
      listar_ficha, encerrar_ano, pessoas, pessoas_faltas
from django.urls.conf import path
urlpatterns = [
    path('pessoas/', pessoas, name="listarpessoas"),
    path('pessoas/<int:pessoa_id>', atualizar_pessoa, name="atualizarpessoa"),
    path('pessoas/<int:pessoa_id>/faltas', pessoas_faltas, name="lancarfalta" ),
    path('pessoas/<int:pessoa_id>/fichas', listar_ficha, name='ficha' ),
    path('pessoas/<int:pessoa_id>/fichas/<int:ano>', gerar_ficha, name='ficha'),
    path('faltas/', faltas, name="listarfaltas"),
    # path('listarpessoas/', listar_pessoas, name='listarpessoas'),
    # path('pessoas/<int:pessoa_id>'),
    # path('fichas/'),
    # path('fichas/<int:pessoa_id>'),
    # path('fichas/<int:pessoa_id>/<int:ano>'),
    # path('faltas/'),
    # path('faltas/<int:falta_id>'),
    # path('faltas/<int:pessoa_id'),
    # path('ficha/<int:pessoa_id>', listar_ficha, name='ficha' ),
    # path('ficha/<int:pessoa_id>&<int:ano>', gerar_ficha, name='ficha' ),
    path('encerrarano/<int:pessoa_id>&<int:ano>', encerrar_ano, name='encerrarano' ),
   
    # path('cadastrartf/', cadastrar_tf, name='cadastrartf'),
    
    # path('lancar/<int:pessoa_id>&<str:pessoa_nome>', lancar_falta, name='lancarfalta'),
   
]