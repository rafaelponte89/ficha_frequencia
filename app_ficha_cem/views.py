from django.shortcuts import render, redirect
from .models import Faltas, Pessoas, Faltas_Pessoas, Pontuacoes
from .forms import formularioPessoa, formularioTF, formularioLF
from django.views import View
from django.contrib import messages
# Create your views here.


from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from datetime import datetime, timedelta
from django.http import HttpResponse

# determina se o ano é bissexto
def bissexto(ano):

    if ano % 400 == 0:
        return True
    else:
        if ano % 4 == 0:
            if ano % 100 == 0:
                return False
            return True

# retorna a quantidade de dias de um determinado ano
def retornar_dias(ano):
    dias    = 365

    if bissexto(ano):
        dias = 366
    
    return dias

def retornar_mes_num(mes_nome):
    meses = {
        'janeiro':[1,31],
        'fevereiro':[2,28],
        'marco':[3,31],
        'abril':[4,30],
        'maio':[5,31],
        'junho':[6,30],
        'julho':[7,31],
        'agosto':[8,31],
        'setembro':[9,30],
        'outubro':[10,31],
        'novembro':[11,30],
        'dezembro':[12,31]
    }
    num_mes = meses[mes_nome]

    return num_mes

def retornar_mes_nome(mes_num):
    meses = {
        1:['janeiro',31],
        2:['fevereiro',28],
        3:['marco',31],
        4:['abril',30],
        5:['maio',31],
        6:['junho',30],
        7:['julho',31],
        8:['agosto',31],
        9:['setembro',30],
        10:['outubro',31],
        11:['novembro',30],
        12:['dezembro',31]
    }
    nome_mes = meses[mes_num]
    return nome_mes

# função recursiva que determina se a data é útil (excluindo sábado e domingo) para o tipo P, senão retorna própria data
def data_util(data, tp='P'):
    
    if tp == 'P':
        if (data.weekday() != 6 and data.weekday() != 5):
            return data
        data = data + timedelta(days=1)
        return data_util(data)
    return data

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

# configurar meses de acordo com a data de admissao de uma pessoa
def configurar_meses_v2(ano, pessoa_id):
    pessoa = Pessoas.objects.get(pk=pessoa_id)
    mes_adm_n = pessoa.admissao.month
    dia_adm = pessoa.admissao.day - 1
    ano_adm = pessoa.admissao.year
    meses = {}
    dias = []

    # construção dos meses
    for i in range(1,13):
        mes = retornar_mes_nome(i)[0]
        qtd_dias = retornar_mes_nome(i)[1]

        if mes == 'fevereiro' and bissexto(ano):
            qtd_dias = 29
        
        for i in range(qtd_dias):
            dias.append(' ')
    
        meses[mes] = dias
        dias = []
    
    # dicionario de meses conforme data de admissao
    if ano == ano_adm:
        for m, dias in meses.items():
            for dia in range(len(dias)):
                if mes_adm_n == retornar_mes_num(m)[0]:
                    if dia_adm <= dia:
                        meses[m][dia] = 'C'
                elif mes_adm_n <= retornar_mes_num(m)[0]:
                    meses[m][dia] = 'C'
                else:
                    meses[m][dia] = ' '
    else:
        if ano >= ano_adm:
            for m, dias in meses.items():
                for dia in range(len(dias)):
                    meses[m][dia] = 'C'
    
    return meses

# faz a pesquisa e incremento para verificar se existe alta lançada naquela data, impedindo lançamento em data
# que já exista falta computada
def lancar_falta(data_lanc, pessoa_id):
    q1 = Faltas_Pessoas.objects.filter(data__year=data_lanc.year)
    q2 = Faltas_Pessoas.objects.filter(pessoa_id=pessoa_id)
    faltas_pessoa = q1.intersection(q2)
    datas = []
    for fp in faltas_pessoa:
        data = fp.data
        for dias in range(1,fp.qtd_dias):
            data += timedelta(days=1)
            data = datetime(data.year, data.month, data.day)
            datas.append(data)
    
   
    data_lanc = datetime(data_lanc.year, data_lanc.month, data_lanc.day)

    # se a data de lancamento já existe, falso para lançamento
    if data_lanc in datas:
        return False
    # se a data de lancamento não existe liberado
    else:
        return True

# fazer o lançamento de faltas para determinada pessoa
def pessoas_faltas(request, pessoa_id):

    pessoa = Pessoas.objects.get(pk=pessoa_id)
    admissao = pessoa.admissao
    data_lancamento = 0

    if request.method == 'POST':
        form = formularioLF(request.POST)
        data_lancamento = form['data'].value()
        data_lancamento = datetime.strptime(data_lancamento, '%Y-%m-%d').date()
      
        if form.is_valid() and data_lancamento > admissao and lancar_falta(data_lancamento, pessoa_id):
        
            form.save()
            messages.success(request,"Falta registrada!")
            return redirect('lancarfalta',pessoa_id)
        else:
            messages.error(request,"Não foi possível registrar a falta!",'danger')
    else:
        form = formularioLF(initial={'pessoa':pessoa})
    return render(request,'template/lancar_falta.html', {'form':form, 'pessoa':pessoa})

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
    return render(request,'template/cadastrar_pessoa.html',{'form':form,'pessoa':pessoa})

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
    return render(request,'template/cadastrar_pessoa.html',{'form':form, 'pessoas':pessoas})

# listar anos de uma determinada pessoa
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
    anos_status = {}
    for ano in anos:
        status  = checar_existencia_pontuacao(ano,pessoa)
        if status:
            status = 'Aberto'
        else:
            status = 'Fechado'
        anos_status[ano] = status
  
    return render(request,'template/listar_ficha.html',{'anos':anos_status, 'pessoa':pessoa})

# ainda não utilizada
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


# def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    
    html = template.render(context_dict)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode('ISO-8859-1')), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

# conta os tipos de faltas construindo um dicionário
def contar_tipos_faltas(faltas):

    # insere no dicionario nova falta e atualiza quantidade da falta
    qtd = 0
    tipo_faltas ={}
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

    return tipo_faltas

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
    return render(request,'template/cadastrar_tipo_falta.html',{'form':form, 'faltas':faltas})

def gerar_ficha(request, pessoa_id, ano, pdf=None):
    
    pessoa = Pessoas.objects.get(pk=pessoa_id)
    meses = configurar_meses(ano)
    meses = configurar_meses_v2(ano,pessoa_id)
    cargo, funcao, ue  = gerar_pontuacao_anual(ano,pessoa)
    cargo_a, funcao_a, ue_a  = gerar_pontuacao_anual(ano,pessoa,'a')
    dias = range(1,32)
    faltas = Faltas_Pessoas.objects.all().order_by('data').filter(data__year=ano).filter(pessoa=pessoa_id)
    admissao = pessoa.admissao
    dia_adm= pessoa.admissao.day
    mes_adm = pessoa.admissao.month
    ano_adm = pessoa.admissao.year
    admissao = f'{dia_adm}/{mes_adm}/{ano_adm}'
    
    tipo_faltas=contar_tipos_faltas(faltas)

    data = ''
    for falta in faltas:
       
        data = falta.data
        
        for d in range(falta.qtd_dias):
              
            if d > 0:
                data = data + timedelta(days=1)

            # retorna as datas úteis se tipo da falta for P, caso contrário retorna a própria data
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
        'dias': dias,
        'tp_faltas': tipo_faltas,
        # 'status': 'aberto',
        'admissao':admissao
        # 'pagesize':'A4'

    }

    # if pdf != None: 
    #     pdf = render_to_pdf('template/ficha_cem.html',contexto)
    #     return HttpResponse(pdf, content_type='application/pdf')
        
    return render(request,'template/ficha_cem.html', {'contexto':contexto})

def index(request):
    return render(request,'template/index.html')

def encerrar_ano(request, pessoa_id, ano):

    pessoa = Pessoas.objects.get(pk=pessoa_id)
    cargo, funcao, ue =   gerar_pontuacao_anual(ano,pessoa)
    cargo_a, funcao_a, ue_a =   gerar_pontuacao_anual(ano,pessoa,'a')
    soma_a = cargo_a + funcao_a + ue_a
    anos, pessoa = listar_anos(pessoa.id)
    
    try:
        if anos.index(ano) == 0 and soma_a == 0:
            pontuacao = Pontuacoes(ano=ano,cargo=cargo,funcao=funcao,ue=ue,pessoa=pessoa)
            pontuacao.save()
            messages.success(request,f"Ano {ano} fechado com sucesso!")
        else: 
            if soma_a != 0:
                pontuacao = Pontuacoes(ano=ano,cargo=cargo,funcao=funcao,ue=ue,pessoa=pessoa)
                pontuacao.save()
                messages.success(request,f"Ano {ano} fechado com sucesso!")
            else:
                messages.info(request,f"Ano fechamento - { ano }! \n Ano anterior {ano-1} aberto!",'primary')

    except:
        # return render(request, 'template/encerrar_ano.html', {'mensagem':mensagem, 'pessoa':pessoa})
        messages.info(request,f'Ano {ano} já fechado!')

            
    return render(request, 'template/encerrar_ano.html', {'pessoa':pessoa})

    
# recupera a pontuação do ano corrente 
def checar_existencia_pontuacao(ano, pessoa):
    status = True
    q2 = Pontuacoes.objects.filter(pessoa=pessoa)
    q3 = Pontuacoes.objects.filter(ano=ano)
    pontuacao = q2.intersection(q3)

    if len(pontuacao):
        status = False
    else:
        status = True

    return  status 

def gerar_pontuacao_anual(ano,pessoa, tipo='c'):
    '''a - ano anterior, c - ano corrente'''

    dias = retornar_dias(ano) # ano corrente

    q1 = Pontuacoes.objects.filter(ano=ano-1) # ano anterior
    q2 = Pontuacoes.objects.filter(pessoa=pessoa)

    pontuacao_anterior = q1.intersection(q2)
    
    # ano anterior
    if tipo == 'a':
        if len(pontuacao_anterior) == 0:
            cargo = 0
            funcao = 0
            ue = 0
           
        else:
            cargo = pontuacao_anterior[0].cargo
            funcao = pontuacao_anterior[0].funcao
            ue = pontuacao_anterior[0].ue
            
    else:
        # ano corrente
        if len(pontuacao_anterior) == 0 :
            cargo = dias
            funcao = dias
            ue = dias
        else:
            cargo = int(pontuacao_anterior[0].cargo) + dias
            funcao = int(pontuacao_anterior[0].funcao) + dias
            ue = int(pontuacao_anterior[0].ue) + dias
             
    return cargo, funcao, ue