from django.shortcuts import render, redirect
from .models import Pessoas
from .forms import formularioPessoa
from django.contrib import messages

# Create your views here.
# atualiza informações de uma pessoa
def atualizar_pessoa(request, pessoa_id):
    pessoa = Pessoas.objects.get(pk=pessoa_id)
   
    if request.method == 'POST':
        form = formularioPessoa(request.POST, instance=pessoa)
        if form.is_valid():
            form.save()
            messages.success(request,"Pessoa atualizada!")
            return redirect('listarpessoas')
    else:
        form = formularioPessoa(instance=pessoa)
    return render(request,'cadastrar_pessoa.html',{'form':form,'pessoa':pessoa})

# listar e incluir pessoas
def pessoas(request):
    pessoas = Pessoas.objects.all()
    
    
    if request.method == 'POST':
        form = formularioPessoa(request.POST)
    
        if form.is_valid():
            form.save()
            messages.success(request,"Pessoa registrada!")
            return redirect('listarpessoas')
    else:

        form = formularioPessoa()
    return render(request,'cadastrar_pessoa.html',{'form':form, 'pessoas':pessoas})
