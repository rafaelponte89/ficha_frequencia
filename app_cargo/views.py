from django.shortcuts import render, redirect
from .models import Cargos
from .forms import formularioCargo
# Create your views here.

def cargos(request):
    cargos = Cargos.objects.all()
    if request.method == 'POST':
        form = formularioCargo(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listarcargos')
    else:
        form = formularioCargo()
    return render(request,'cadastrar_cargo.html',{'form':form, 'cargos':cargos})


