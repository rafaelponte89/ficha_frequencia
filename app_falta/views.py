from django.shortcuts import render, redirect
from .forms import formularioTF
from .models import Faltas

# Create your views here.

# listar e incluir faltas
def faltas(request):
    faltas = Faltas.objects.all()
    if request.method == 'POST':
        form = formularioTF(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listarfaltas')
    else:
        form = formularioTF()
    return render(request,'cadastrar_tipo_falta.html',{'form':form, 'faltas':faltas})