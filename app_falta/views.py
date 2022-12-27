from django.shortcuts import render, redirect
from .forms import formularioTF
from .models import Faltas
from django.contrib import messages

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

def atualizar_faltas(request, falta_id):
    faltas = Faltas.objects.all()
    falta = Faltas.objects.get(pk=falta_id)
    
    if request.method == 'POST':
        form = formularioTF(request.POST, instance=falta)
        if form.is_valid():
            form.save()
            messages.success(request,"Falta atualizada!")

            return redirect('listarfaltas')
    else:
        form = formularioTF(instance=falta)

    
    return render(request,'cadastrar_tipo_falta.html',{'form':form, 'faltas':faltas})