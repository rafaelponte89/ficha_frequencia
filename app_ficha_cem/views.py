from django.shortcuts import render, redirect
from .models import Faltas, Pessoas, Faltas_Pessoas, Pontuacoes
from .forms import formularioPessoa, formularioTF, formularioLF
from django.views import View
# Create your views here.


from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from datetime import datetime, timedelta
from django.http import HttpResponse

def bissexto(ano):
    if ano % 400 == 0:
        return True
    else:
        if ano % 4 == 0:
            if ano % 100 == 0:
                return False
            return True



def faltas(request):
    faltas = Faltas.objects.all()
    if request.method == 'POST':
        form = formularioTF(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listarfaltas')
    else:
        form = formularioTF()
    return render(request,'template/cadastrar_tipo_falta.html',{'form':form, 'faltas':faltas})

def pessoas_faltas(request, pessoa_id):

    pessoa = Pessoas.objects.get(pk=pessoa_id)
    pessoa_faltas = Faltas_Pessoas.objects.all()


    if request.method == 'POST':
        form = formularioLF(request.POST)
    
        if form.is_valid():
            form.save()
            return redirect('lancarfalta',pessoa_id)
    else:
        form = formularioLF(initial={'pessoa':pessoa})
    return render(request,'template/lancar_falta.html', {'form':form, 'pessoa':pessoa})

def atualizar_pessoa(request, pessoa_id):
    pessoa = Pessoas.objects.get(pk=pessoa_id)
   
    if request.method == 'POST':
        form = formularioPessoa(request.POST, instance=pessoa)
        if form.is_valid():
            form.save()
            return redirect('listarpessoas')
    else:
        form = formularioPessoa(instance=pessoa)
    return render(request,'template/cadastrar_pessoa.html',{'form':form,'pessoa':pessoa})


def pessoas(request):
    pessoas = Pessoas.objects.all()

    if request.method == 'POST':
        form = formularioPessoa(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listarpessoas')
    else:

        form = formularioPessoa()
    return render(request,'template/cadastrar_pessoa.html',{'form':form, 'pessoas':pessoas})





def listar_anos(pessoa_id):
    anos = []
    pessoa_faltas = Faltas_Pessoas.objects.all()
    pessoa = Pessoas.objects.get(pk=pessoa_id)
    for i in pessoa_faltas:
        if i.data.year not in anos and i.pessoa.id == pessoa_id:
            anos.append(i.data.year)
    return anos, pessoa

def listar_ficha(request, pessoa_id):

    anos, pessoa = listar_anos(pessoa_id)

    return render(request,'template/listar_ficha.html',{'anos':anos, 'pessoa':pessoa})

def retornar_dias(ano):
    dias    = 365

    if bissexto(ano):
        dias = 366
    
    return dias

# configurar meses
def configurar_meses(ano):
    
    meses_31 = ['C','C','C','C','C','C','C','C','C','C','C','C','C','C','C', 'C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C']
    meses_30 = ['C','C','C','C','C','C','C','C','C','C','C','C','C','C','C', 'C','C','C','C','C','C','C','C','C','C','C','C','C','C','C',' ']
    fevereiro = ['C','C','C','C','C','C','C','C','C','C','C','C','C','C','C', 'C','C','C','C','C','C','C','C','C','C','C','C','C']
    
    if bissexto(ano):
        fevereiro.append('C')
       

    meses = {
        'janeiro': meses_31.copy(),
        'fevereiro': fevereiro,
        'marco': meses_31.copy(),
        'abril': meses_30.copy(),
        'maio': meses_31.copy(),
        'junho': meses_30.copy(),
        'julho' : meses_31.copy(),
        'agosto': meses_31.copy(),
        'setembro': meses_30.copy(),
        'outubro': meses_31.copy(),
        'novembro': meses_30.copy(),
        'dezembro': meses_31.copy()
    }

    return meses

def faltas_a_descontar(ano,pessoa):
    # atribuição 
    maior = Faltas_Pessoas.objects.all().filter(data__gte=f'{ano-1}-11-01')
    maior = maior.filter(pessoa=pessoa)
    menor = Faltas_Pessoas.objects.all().filter(data__lte=f'{ano}-10-31')
    menor = menor.filter(pessoa=pessoa)
    atrib = maior.intersection(menor)

    n_faltas = 0

    for a in atrib:
        if a.falta.tipo in ['J','AM']:
            n_faltas += 1
    
    return n_faltas


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    
    html = template.render(context_dict)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode('ISO-8859-1')), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def gerar_ficha(request, pessoa_id, ano, pdf=None):
    
    pessoa = Pessoas.objects.get(pk=pessoa_id)
    meses = configurar_meses(ano)
    cargo, funcao, ue, pontuacao  = recuperar_pontuacao_anual(ano,pessoa)
    cargo_a, funcao_a, ue_a  = gerar_pontuacao_anual(ano,pessoa,'a')
    dias = range(1,32)
    tipo_faltas = {}
    faltas = Faltas_Pessoas.objects.all().order_by('data').filter(data__year=ano).filter(pessoa=pessoa_id)
    
    # for d in faltas:
    #     print(d.falta.tipo, d.qtd_dias, d.data)


    # insere no dicionario nova falta e atualiza quantidade da falta
    qtd = 0
    for f in faltas:
        sigla = f.falta.tipo
        descricao = f.falta.descricao
      
        if sigla not in tipo_faltas.keys():
           qtd = f.qtd_dias
           tipo_faltas[sigla] = [descricao, qtd]
        else:
            qtd = tipo_faltas[sigla][1]
            qtd += f.qtd_dias
            tipo_faltas[sigla][1] = qtd

    data = ''
    for falta in faltas:
       
        data = falta.data
        
        for d in range(falta.qtd_dias):
              
            if d > 0:
                data = data + timedelta(days=1)
            
            # retorna as data úteis se tipo da falta for P, caso contrário retorna a própria data
            data = data_util(data, falta.falta.tipo)

            mes = data.month
            dia = data.day - 1
            
            if mes == 1:
                meses['janeiro'][dia] = falta.falta.tipo
            elif mes == 2:
                meses['fevereiro'][dia] = falta.falta.tipo
            elif mes == 3:
                meses['marco'][dia] = falta.falta.tipo
            elif mes == 4:
                meses['abril'][dia] = falta.falta.tipo
            elif mes == 5:
                meses['maio'][dia] = falta.falta.tipo
            elif mes == 6:
                meses['junho'][dia] = falta.falta.tipo
            elif mes == 7:
                meses['julho'][dia] = falta.falta.tipo
            elif mes == 8:
                meses['agosto'][dia] = falta.falta.tipo
            elif mes == 9:
                meses['setembro'][dia] = falta.falta.tipo
            elif mes == 10:
                meses['outubro'][dia] = falta.falta.tipo
            elif mes == 11:
                meses['novembro'][dia] = falta.falta.tipo
            elif mes == 12:
                meses['dezembro'][dia] = falta.falta.tipo
    
    
    contexto = {
        'meses': meses,
        'ano': ano,
        'funcao': funcao,
        'cargo': cargo,
        'ue': ue,
        'funcao_a': funcao_a,
        'cargo_a': cargo_a,
        'ue_a': ue_a,
        'nome': pessoa.nome,
        'pessoa': pessoa,
        'pontuacao': pontuacao,
        'dias': dias,
        'tp_faltas': tipo_faltas,
        # 'pagesize':'A4'

    }

    if pdf != None: 
        pdf = render_to_pdf('template/ficha_cem.html',contexto)
        return HttpResponse(pdf, content_type='application/pdf')
        
    return render(request,'template/ficha_cem.html', {'contexto':contexto})

# função recursiva que determina se a data é útil para o tipo P, senão retorna própria data
def data_util(data, tp='P'):
    
    if tp == 'P':
        if (data.weekday() != 6 and data.weekday() != 5):
            return data
        data = data + timedelta(days=1)
        return data_util(data)
    return data
   
   
   
def index(request):
    return render(request,'template/index.html')

def encerrar_ano(request, pessoa_id, ano):
    status = f'Ano {ano} não Encerrado! Existem anos anteriores em aberto!'
    pessoa = Pessoas.objects.get(pk=pessoa_id)
    cargo, funcao, ue =   gerar_pontuacao_anual(ano,pessoa)
    cargo_a, funcao_a, ue_a =   gerar_pontuacao_anual(ano,pessoa,'a')
    soma_a = cargo_a + funcao_a + ue_a
    anos, pessoa = listar_anos(pessoa.id)

    
    
    if anos.index(ano) == 0 and soma_a == 0:
        pontuacao = Pontuacoes(ano=ano,cargo=cargo,funcao=funcao,ue=ue,pessoa=pessoa)
        pontuacao.save()
        status = f'Ano {ano} Encerrado!'
    else: 
        if soma_a != 0:
            pontuacao = Pontuacoes(ano=ano,cargo=cargo,funcao=funcao,ue=ue,pessoa=pessoa)
            pontuacao.save()
            status = f'Ano {ano} Encerrado!'

    contexto = {
        'ano': ano,
        'pessoa':pessoa,
        'status': status
    }
    
    
    return render(request, 'template/encerrar_ano.html', {'contexto': contexto})

def recuperar_pontuacao_anual(ano, pessoa):
    status = True
    q2 = Pontuacoes.objects.filter(pessoa=pessoa)
    q3 = Pontuacoes.objects.filter(ano=ano)
    pontuacao = q2.intersection(q3)

    if len(pontuacao):
        cargo, funcao, ue = pontuacao[0].cargo, pontuacao[0].funcao, pontuacao[0].ue
        status = False
    else:
        cargo, funcao, ue = 0,0,0

    return cargo, funcao, ue, status 

def gerar_pontuacao_anual(ano,pessoa, tipo='n'):

   
    dias = retornar_dias(ano)
    q1 = Pontuacoes.objects.filter(ano=ano-1)
    q2 = Pontuacoes.objects.filter(pessoa=pessoa)
    pontuacao_anterior = q1.intersection(q2)
    
    
    if tipo == 'a':
        if len(pontuacao_anterior) == 0:
            cargo = 0
            funcao = 0
            ue = 0
           
        else:
            cargo = pontuacao_anterior[0].cargo
            funcao = pontuacao_anterior[0].cargo
            ue = pontuacao_anterior[0].cargo
            
    else:
        if len(pontuacao_anterior) == 0 :
            cargo = dias
            funcao = dias
            ue = dias
        if len(pontuacao_anterior) > 0:
             cargo = int(pontuacao_anterior[0].cargo) + dias
             funcao = int(pontuacao_anterior[0].funcao) + dias
             ue = int(pontuacao_anterior[0].ue) + dias
             
    return cargo, funcao, ue