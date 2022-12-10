from django.urls.conf import path
from .views import faltas

urlpatterns = [
          path('', faltas, name='listarfaltas'),
]