from django.urls.conf import path
from .views import cargos

urlpatterns = [
     path('', cargos, name='listarcargos'),
]