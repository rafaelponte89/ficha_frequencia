from .views import gerar_ficha, abrir_ano, \
      listar_ficha, encerrar_ano, pessoas_faltas, pdf_v2, lancar_pontuacoes, atualizar_pontuacoes, excluir_pontuacoes
from django.urls.conf import path,include
urlpatterns = [
    path('pessoas/',include('app_pessoa.urls')),
    path('pessoas/<str:pessoa_id>/faltas', pessoas_faltas, name="lancarfalta" ),
    path('pessoas/<str:pessoa_id>/pontuacoes', lancar_pontuacoes, name='lancarpontuacao'),
    path('pessoas/<str:pessoa_id>/pontuacoes/<str:pontuacao_id>', atualizar_pontuacoes, name='atualizarpontuacao'),
    path('pessoas/<str:pessoa_id>/pontuacoes/<str:pontuacao_id>/apagar', excluir_pontuacoes, name='excluirpontuacao'),
    path('pessoas/<str:pessoa_id>/fichas', listar_ficha, name='listarficha' ),
    path('pessoas/<str:pessoa_id>/fichas/<int:ano>', gerar_ficha, name='ficha'),
    path('pessoas/<str:pessoa_id>/fichas/encerrar/<int:ano>', encerrar_ano, name='encerrarano' ),
    path('pessoas/<str:pessoa_id>/fichas/abrir/<int:ano>', abrir_ano, name='abrirano' ),
    path('pessoas/<int:pessoa_id>/fichas/<int:ano>/', pdf_v2, name='baixarpdf'),
    path('faltas/', include('app_falta.urls')),
    path('cargos/',include('app_cargo.urls')),   
]