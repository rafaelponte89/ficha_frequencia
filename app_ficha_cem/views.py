from django.shortcuts import render, redirect
from .models import Faltas, Faltas_Pessoas, Pontuacoes
from .forms import formularioLF, formularioPontuacao
from django.views import View
from django.contrib import messages
from app_pessoa.models import Pessoas

# Create your views here.

from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from datetime import datetime, timedelta
from django.http import HttpResponse
import reportlab
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

def retornar_mes_num(mes_nome, ano):
    meses = {
        'janeiro':[1,31],
        'fevereiro':[2,29 if bissexto(ano) else 28],
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
    meses_30 = ['C','C','C','C','C','C','C','C','C','C','C','C','C','C','C', 'C','C','C','C','C','C','C','C','C','C','C','C','C','C','C']
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

# configurar meses de acordo com a data de admissao de uma pessoa
def configurar_meses_v3(ano, pessoa_id):
    pessoa = Pessoas.objects.get(pk=pessoa_id)
    mes_adm = pessoa.admissao.month
    dia_adm = pessoa.admissao.day - 1
    ano_adm = pessoa.admissao.year

    meses = criar_estrutura_meses() 

    # dicionario de meses conforme data de admissao
    if ano == ano_adm:
        for m, dias in meses.items():
            qtd_dias = retornar_mes_num(m)[1]
            if m == 'fevereiro' and bissexto(ano):
                qtd_dias = 29
        
            for dia in range(qtd_dias):
                if mes_adm == retornar_mes_num(m)[0]:
                    if dia_adm <= dia:
                        meses[m][dia] = 'C'
                elif mes_adm <= retornar_mes_num(m)[0]:
                    meses[m][dia] = 'C'
    else:
        if ano >= ano_adm:
            for m, dias in meses.items():
                qtd_dias = retornar_mes_num(m)[1]
                if m == 'fevereiro' and bissexto(ano):
                    qtd_dias = 29
                for dia in range(qtd_dias):
                    meses[m][dia] = 'C'
    
    return meses

def criar_estrutura_meses():

    estrutura_meses_nome = {}
   

    dias = []
    # construção dos meses
    for i in range(1,13):
        mes = retornar_mes_nome(i)[0]
        for j in range(31):
            dias.append('-')
        estrutura_meses_nome[mes] = dias
        
        dias = []

    return estrutura_meses_nome
# configurar meses de acordo com a data de admissao de uma pessoa
def configurar_meses_v4(ano, pessoa_id):
    '''A versão atual do método leva em consideração data de admissão e saída para fazer a devida configuração'''
    pessoa = Pessoas.objects.get(pk=pessoa_id)
    mes_adm = pessoa.admissao.month
    dia_adm = pessoa.admissao.day - 1
    ano_adm = pessoa.admissao.year

    mes_saida = 0
    dia_saida = 0
    ano_saida = 0
    if pessoa.saida != None:
        mes_saida = pessoa.saida.month
        dia_saida = pessoa.saida.day
        ano_saida = pessoa.saida.year

    meses = criar_estrutura_meses()

    #dicionario de meses conforme data de admissao
    if ano_adm == ano and ano_saida == ano:
        for mes in meses:
                qtd_dias = retornar_mes_num(mes,ano)[1]
                if mes_adm == retornar_mes_num(mes,ano)[0]:
                    for dia in range(qtd_dias):
                        if dia >= dia_adm:
                            meses[mes][dia] = 'C'
                else:
                    if mes_adm < retornar_mes_num(mes,ano)[0] and mes_saida > retornar_mes_num(mes,ano)[0]:
                        for dia in range(qtd_dias):
                            meses[mes][dia] = 'C'
                    else:
                        if mes_saida == retornar_mes_num(mes,ano)[0]:
                            for dia in range(qtd_dias):
                                if dia < dia_saida:
                                    meses[mes][dia] = 'C'

    else:
        if ano == ano_adm:
            for mes in meses:
                qtd_dias = retornar_mes_num(mes,ano)[1]
                if mes_adm == retornar_mes_num(mes,ano)[0]:
                    for dia in range(qtd_dias):
                        if dia >= dia_adm:
                            meses[mes][dia] = 'C'
                else:
                    if mes_adm < retornar_mes_num(mes,ano)[0]:
                        for dia in range(qtd_dias):
                            meses[mes][dia] = 'C'
            
        elif ano == ano_saida:
            for mes in meses:
                qtd_dias = retornar_mes_num(mes,ano)[1]
                if mes_saida == retornar_mes_num(mes,ano)[0]:
                    for dia in range(qtd_dias):
                        if dia < dia_saida:
                            meses[mes][dia] = 'C'
                else:
                    if mes_saida > retornar_mes_num(mes,ano)[0]:
                        for dia in range(qtd_dias):
                            meses[mes][dia] = 'C'
            
        else:
           if ano_adm != ano and ano_saida != ano:
                for mes in meses:
                    qtd_dias = retornar_mes_num(mes,ano)[1]

                    for dia in range(qtd_dias):
                        meses[mes][dia] = 'C'
  
    
    return meses


def gerar_lancamento_em_memoria(data_lanc,qtd_dias):
    '''Atraves da data de lancamento e quantidade de dias gera um dicionario ano a ano com as devidas datas'''
    # Ex. anos[2020] = [(mes,dia,ano),(mes,dia,ano)], anos[2021]=[(mes, dia, ano)]
    anos = {}
    data = data_lanc

    for dia in range(0,qtd_dias):
        
        if data.year not in anos.keys():
            anos[data.year] = [data]
        
        else:
            anos[data.year].append(data)
        
        data += timedelta(days=1)
    
    return anos


def verificar_status_ano(ano, pessoa_id):
    pontuacao = Pontuacoes.objects.filter(pessoa=pessoa_id).filter(ano=ano)
    ano_fechado = True

    if pontuacao.count() == 0:
        ano_fechado = False
    
    return ano_fechado


# faz a pesquisa e incremento para verificar se existe falta lançada naquela data, impedindo lançamento em data
# que já exista falta computada
def lancar_falta(data_lanc, qtd_dias, pessoa_id):
    # pontuacao = Pontuacoes.objects.filter(pessoa=pessoa_id).filter(ano=data_lanc.year)
    conflito = True
    # ano_fechado = True
   
   
    q1 = Faltas_Pessoas.objects.filter(data__year=data_lanc.year)
    q2 = Faltas_Pessoas.objects.filter(pessoa_id=pessoa_id)
    faltas_pessoa = q1.intersection(q2)
    datas = []
    for fp in faltas_pessoa:
        data = fp.data
        for dias in range(0,fp.qtd_dias):
            data = datetime(data.year, data.month, data.day)
            datas.append(data)
            data += timedelta(days=1)
                
    data_lanc = datetime(data_lanc.year, data_lanc.month, data_lanc.day)
    datas_lanc = []

    for dias in range(0,qtd_dias):
        datas_lanc.append(data_lanc)
        data_lanc += timedelta(days=1)

    # if pontuacao.count() == 0:
    #     ano_fechado = False
        
    for lancamento in datas_lanc:
        if lancamento in datas:
            conflito = False
            break
            
    # return conflito, ano_fechado
    return conflito

# fazer o lançamento de faltas para determinada pessoa
def pessoas_faltas(request, pessoa_id):

    pessoa = Pessoas.objects.get(pk=pessoa_id)
    pessoa_falta = Faltas_Pessoas.objects.filter(pessoa=pessoa).order_by('data')[:30]
    admissao = pessoa.admissao
    saida = pessoa.saida
    data_lancamento = 0
   
    if request.method == 'POST':
        # instância do formulário para pegar dados
        form = formularioLF(request.POST)
        
        # pegar valores do formulário
        qtd_dias = int(form.data['qtd_dias'])
        data_lancamento = form['data'].value()
        falta = Faltas.objects.get(pk=form['falta'].value())
       
        data_lancamento = datetime.strptime(data_lancamento, '%Y-%m-%d').date()

        # criar intervalos de lançamentos na memória e dividir por ano (ano é chave)
        dia_mes_ano = gerar_lancamento_em_memoria(data_lancamento,qtd_dias)
       
        # verifica se os dados preenchidos são válidos
        # verifica se existe faltas naquele intervalo
        # conflito, ano_fechado = lancar_falta(data_lancamento, qtd_dias ,pessoa_id)
        conflito = lancar_falta(data_lancamento, qtd_dias, pessoa_id)
        ano_fechado = verificar_status_ano(data_lancamento.year,pessoa_id)
      
        if form.is_valid() and data_lancamento > admissao and data_lancamento <= saida:
            
            if conflito:
                if not ano_fechado:
                    # navega entre as chaves (ano)
                    for k in dia_mes_ano.keys():
                        qtd_dias = len(dia_mes_ano[k]) # quantos dias existem dentro da chave ano
                        data_lancamento = dia_mes_ano[k][0] # pega o primeiro dia do lançamento e depois o primeiro dia do ano

                        # cria objeto com os novos dados
                        novoObj = Faltas_Pessoas(pessoa=pessoa,data=data_lancamento,qtd_dias=qtd_dias,falta=falta)
                        
                        # salva o objeto
                        novoObj.save()
            
                    messages.success(request,"Falta registrada!")
                    return redirect('lancarfalta',pessoa_id)
                else:
                    messages.error(request,f"Ano {data_lancamento.year} Fechado! Abrir se deseja efetuar lançamentos!",'danger')

            else:
                messages.error(request,"Não foi possível registrar a falta! Pode existir conflito de datas!",'danger')
        else:
            messages.warning(request,f"Precisa estar no Intervalo da Admissão e Saída!  Data Admissão: {admissao.strftime('%d/%m/%Y')} Data Saída: {saida.strftime('%d/%m/%y')}")

    else:
        
        form = formularioLF(initial={'pessoa':pessoa})
    return render(request,'template/lancar_falta.html', {'form':form, 'pessoa':pessoa, 'faltas':pessoa_falta})


def excluir_pessoas_faltas(request, pessoa_id, lancamento_id):

    lancamento = Faltas_Pessoas.objects.filter(pk=lancamento_id)
    pessoa = Pessoas.objects.get(pk=pessoa_id)
    pessoa_falta = Faltas_Pessoas.objects.filter(pessoa=pessoa).order_by('data')[:30]

    if request.method == 'GET':
        lancamento.delete()    
        messages.success(request,"Lançamento Apagado!")
        return redirect('lancarfalta',pessoa_id)
    else:
        form = formularioPontuacao(initial={'pessoa':pessoa})
    
    return render(request,'template/lancar_falta.html', {'form':form, 'pessoa':pessoa, 'faltas':pessoa_falta})
        
# listar anos de uma determinada pessoa
def listar_anos(pessoa_id):
    anos = []
    pessoa_faltas = Faltas_Pessoas.objects.all()
    pessoa = Pessoas.objects.get(pk=pessoa_id)

    for i in pessoa_faltas:
        if i.data.year not in anos and i.pessoa.id == pessoa_id:
            anos.append(i.data.year)

    return anos[-5:], pessoa

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
  
    return render(request,'template/listar_ficha_v2.html',{'anos':anos_status, 'pessoa':pessoa})

# desconta faltas conforme a data inicial e data final levando em conta 
# a tolerancia 
def faltas_a_descontar(ano,pessoa, tolerancia=6):
    # atribuição 
    data_inicial = datetime(ano-1,11,1)
    data_final = datetime(ano,10,31)
    maior = Faltas_Pessoas.objects.all().filter(data__gte=f'{ano-1}-11-01')
    maior = maior.filter(pessoa=pessoa)
    menor = Faltas_Pessoas.objects.all().filter(data__lte=f'{ano}-10-31')
    menor = menor.filter(pessoa=pessoa)
    atrib = maior.intersection(menor)
    datas = []
   
    for fp in atrib:
        if fp.falta.tipo in ['J','AM']:
            data = datetime(fp.data.year, fp.data.month, fp.data.day)
            
            for dias in range(1,fp.qtd_dias):
                if data >= data_inicial and data <= data_final:
                    datas.append(data)
                data += timedelta(days=1)
                data = datetime(data.year, data.month, data.day)
            else:
                if data >= data_inicial and data <= data_final:
                    datas.append(data)
               
    n_faltas = len(datas)
  
    if n_faltas >= tolerancia:
        n_faltas -= tolerancia
    else:
        n_faltas = 0

    return n_faltas

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

def faltas_por_mes_v2(meses):
    '''Guarda dados de comparecimento e todos os tipos de faltas que ocorreram e suas quantidades, torna uniforme a todos os meses'''
    faltas_por_mes = {}
    faltas_por_mes_n = {}

    for k,v in meses.items():
        for i in v:
            if i != '-':
                faltas_por_mes_n[i] = 0
        
    for k,v in meses.items():
        if k not in faltas_por_mes:
            faltas_por_mes[k] = faltas_por_mes_n.copy()
        for i in v:
            if i != '-':
                faltas_por_mes[k][i] += 1
               
    return faltas_por_mes
    
def faltas_por_mes(meses):
    '''Guarda as faltas referentes somente aos meses em que elas aparecem, não guarda armazenamentos'''
    faltas_por_mes = {}
    for k,v in meses.items():
        if k not in faltas_por_mes:
            faltas_por_mes[k] = {}
       
        for i in v:
            if i != 'C' and i != ' ':
             
                if i not in faltas_por_mes[k]:
                    faltas_por_mes[k][i] = 1
                else:
                    faltas_por_mes[k][i] += 1
    return faltas_por_mes

def consultar_pontuacao(pessoa_id, ano,num=0):
    pontuacao = Pontuacoes.objects.filter(pessoa=pessoa_id).filter(ano=ano-num)
    
    if pontuacao.count():
        cargo = pontuacao[0].cargo
        funcao = pontuacao[0].funcao
        ue = pontuacao[0].ue
    else:
        cargo = 0
        funcao = 0
        ue = 0

    return funcao,cargo,ue

def transformar_em_um_dicionario(funcao,cargo,ue):
    
    meses_pontuacao = {}
    cargo_lst = []
    funcao_lst = []
    ue_lst = []
    for v in cargo.values():
        cargo_lst.append(v)
    
    for v in funcao.values():
        funcao_lst.append(v)

    for v in ue.values():
        ue_lst.append(v)

    i = 0
    for k, v in cargo.items():
        meses_pontuacao[k] = [funcao_lst[i],cargo_lst[i], ue_lst[i]]
        i = i + 1

    return meses_pontuacao

def buscar_informacoes_ficha_v2(pessoa_id, ano):
    anos, pessoa = listar_anos(pessoa_id)
    pessoa = Pessoas.objects.get(pk=pessoa_id)
    meses = configurar_meses_v4(ano,pessoa_id)
    funcao, cargo, ue  = gerar_pontuacao_anual_v2(ano,pessoa)
    funcao_a, cargo_a, ue_a = consultar_pontuacao(pessoa_id, ano, 1)
    ano_a = ano - 1
    meses_pontuacao = transformar_em_um_dicionario(funcao,cargo,ue)
    
    print(meses,'na ficha')
    ano_st = consultar_anos_status(pessoa.id)
    ano_status = ano_st[0][ano]

    dias = []
    for dia in range(1,32):
        dias.append(dia)
   
    faltas = Faltas_Pessoas.objects.all().order_by('data').filter(data__year=ano).filter(pessoa=pessoa_id)
    admissao = pessoa.admissao
    saida = pessoa.saida

    conta = 0
    for l in str(pessoa.cargo):
        if l == '-':
            conta +=1

    if conta > 1:
        cargo_disciplina = str(pessoa.cargo).replace('-','')
        cargo_disciplina = cargo_disciplina + ' - N/A'
        cargo_disciplina = tuple(cargo_disciplina.split('-'))
    elif conta == 0:
        cargo_disciplina = str(pessoa.cargo) + ' - N/A'
        cargo_disciplina = tuple(cargo_disciplina.split('-'))
    else:
        cargo_disciplina = tuple(str(pessoa.cargo).split('-'))

    des_cargo, disciplina = cargo_disciplina
 
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


    faltas_mes_a_mes = faltas_por_mes_v2(meses)            
    
    pessoa.cpf = f'{pessoa.cpf[:3]}.{pessoa.cpf[3:6]}.{pessoa.cpf[6:9]}-{pessoa.cpf[-2:]}'
    
    if pessoa.efetivo:
        pessoa.efetivo='Sim'
    else:
        pessoa.efetivo='Não'

    contexto = {
        'ano_a':ano_a,
        'ano_status':ano_status,
        'meses': meses,
        'falta_por_mes': faltas_mes_a_mes,
        'ano': ano,
        'funcao': funcao,
        'cargo': cargo,
        'ue': ue,
        'des_cargo':des_cargo,
        'disciplina': disciplina,
        'funcao_a': funcao_a,
        'cargo_a': cargo_a,
        'ue_a': ue_a,
        'nome': pessoa.nome,
        'pessoa': pessoa,
        'dias': dias,
        'tp_faltas': tipo_faltas,
        'admissao':admissao,
        'saida':saida,
        'anos':anos,
        'meses_pontu': meses_pontuacao
        # 'pagesize':'A4'

    }
    
    return contexto


# criação 25/12/2022
def buscar_informacoes_ficha_v3(pessoa_id, ano):
    anos, pessoa = listar_anos(pessoa_id)
    pessoa = Pessoas.objects.get(pk=pessoa_id)
    meses = configurar_meses_v4(ano,pessoa_id)
    funcao, cargo, ue  = gerar_pontuacao_anual_v2(ano,pessoa)
    funcao_a, cargo_a, ue_a = consultar_pontuacao(pessoa_id, ano, 1)
    ano_a = ano - 1
    meses_pontuacao = transformar_em_um_dicionario(funcao,cargo,ue)
    
    print(funcao,cargo,ue,'funcao_cargo_ue')

    meses_copy = meses.copy()
    
    # for mes, dias in meses_copy.items():
    #     for m, pontuacao in meses_pontuacao.items():
    #         if mes == m:
    #             dias.extend(pontuacao)
   

    # print(meses)


    ano_st = consultar_anos_status(pessoa.id)
    ano_status = ano_st[0][ano]

    dias = []
    for dia in range(1,32):
        dias.append(dia)
   
    faltas = Faltas_Pessoas.objects.all().order_by('data').filter(data__year=ano).filter(pessoa=pessoa_id)
    admissao = pessoa.admissao
    saida = pessoa.saida

    conta = 0
    for l in str(pessoa.cargo):
        if l == '-':
            conta +=1

    if conta > 1:
        cargo_disciplina = str(pessoa.cargo).replace('-','')
        cargo_disciplina = cargo_disciplina + ' - N/A'
        cargo_disciplina = tuple(cargo_disciplina.split('-'))
    elif conta == 0:
        cargo_disciplina = str(pessoa.cargo) + ' - N/A'
        cargo_disciplina = tuple(cargo_disciplina.split('-'))
    else:
        cargo_disciplina = tuple(str(pessoa.cargo).split('-'))

    des_cargo, disciplina = cargo_disciplina
 
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


    faltas_mes_a_mes = faltas_por_mes_v2(meses)  

    print(faltas_mes_a_mes)          
    
    pessoa.cpf = f'{pessoa.cpf[:3]}.{pessoa.cpf[3:6]}.{pessoa.cpf[6:9]}-{pessoa.cpf[-2:]}'
    
    if pessoa.efetivo:
        pessoa.efetivo='Sim'
    else:
        pessoa.efetivo='Não'

    contexto = {
        'ano_a':ano_a,
        'ano_status':ano_status,
        'meses': meses,
        'falta_por_mes': faltas_mes_a_mes,
        'ano': ano,
        'funcao': funcao,
        'cargo': cargo,
        'ue': ue,
        'des_cargo':des_cargo,
        'disciplina': disciplina,
        'funcao_a': funcao_a,
        'cargo_a': cargo_a,
        'ue_a': ue_a,
        'nome': pessoa.nome,
        'pessoa': pessoa,
        'dias': dias,
        'tp_faltas': tipo_faltas,
        'admissao':admissao,
        'saida':saida,
        'anos':anos,
        'meses_pontu': meses_pontuacao
        # 'pagesize':'A4'

    }
    
    return contexto

def gerar_ficha(request, pessoa_id, ano):
    
    contexto = buscar_informacoes_ficha_v3(pessoa_id, ano)
    return render(request,'template/ficha_cem _v2.html', {'contexto':contexto})

def index(request):
    
    return render(request,'template/index.html')

# recupera a pontuação do ano corrente 
def checar_existencia_pontuacao(ano, pessoa):
    status = True
    q2 = Pontuacoes.objects.filter(pessoa=pessoa)
    q3 = Pontuacoes.objects.filter(ano=ano)
    pontuacao = q2.intersection(q3)


    if pontuacao.count():
        status = False
    else:
        status = True

    return  status 

def contar_dias(data_inicial, data_final):
    dias = (data_final - data_inicial ).days + 1

    return dias

def gerar_pontuacao_atribuicao(ano,pessoa, tipo='c'):
    '''a - ano anterior, c - ano corrente '''

    data_bas_ini = datetime.strptime(f'{ano-1}-11-01','%Y-%m-%d',).date()
    data_bas_fim = datetime.strptime(f'{ano}-10-31','%Y-%m-%d').date()

    if pessoa.admissao > data_bas_ini:
        data_bas_ini = pessoa.admissao

    dias = contar_dias(data_bas_ini, data_bas_fim)
    
    # q1 = PontuacoesAtribuicoes.objects.filter(ano=ano-1) # ano anterior
    # q2 = PontuacoesAtribuicoes.objects.filter(pessoa=pessoa)

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
            cargo = pontuacao_anterior[0].cargo_atrib
            funcao = pontuacao_anterior[0].funcao_atrib
            ue = pontuacao_anterior[0].ue_atrib
 
    else:
        # ano corrente
        if len(pontuacao_anterior) == 0 :
            cargo = dias -faltas_a_descontar(ano,pessoa)
            funcao = dias - faltas_a_descontar(ano,pessoa)
            ue = dias - faltas_a_descontar(ano,pessoa)
        else:
            cargo = int(pontuacao_anterior[0].cargo_atrib) + dias - faltas_a_descontar(ano,pessoa)
            funcao = int(pontuacao_anterior[0].funcao_atrib) + dias - faltas_a_descontar(ano,pessoa)
            ue = int(pontuacao_anterior[0].ue_atrib) + dias - faltas_a_descontar(ano,pessoa)
             
    return cargo, funcao, ue

def gerar_pontuacao_anual(ano,pessoa, tipo='c'):
    '''a - ano anterior, c - ano corrente '''

    data_bas_ini = datetime.strptime(f'{ano}-01-01','%Y-%m-%d',).date()
    data_bas_fim = datetime.strptime(f'{ano}-12-31','%Y-%m-%d').date()

    if pessoa.admissao > data_bas_ini:
        data_bas_ini = pessoa.admissao

    dias = contar_dias(data_bas_ini, data_bas_fim)
    
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
        if  pontuacao_anterior.count() == 0 :
            cargo = dias
            funcao = dias
            ue = dias
        else:
            cargo = pontuacao_anterior[0].cargo + dias
            funcao = pontuacao_anterior[0].funcao + dias
            ue = pontuacao_anterior[0].ue + dias
             
    return cargo, funcao, ue

def gerar_pontuacao_anual_v2(ano,pessoa):
    pontuacao = Pontuacoes.objects.filter(pessoa=pessoa).filter(ano=ano-1)
    acumulado_funcao, acumulado_cargo, acumulado_ue = 0,0,0
    if pontuacao.count():
        acumulado_funcao = pontuacao[0].funcao
        acumulado_cargo = pontuacao[0].cargo
        acumulado_ue = pontuacao[0].ue
    else:
        acumulado_funcao = 0
        acumulado_cargo = 0
        acumulado_ue = 0
        
    funcao = acumular_dias(ano,pessoa.id,acumulado_funcao)
    cargo = acumular_dias(ano,pessoa.id,acumulado_cargo)
    ue = acumular_dias(ano,pessoa.id,acumulado_ue)
    
    return funcao, cargo, ue

#em desenvolvimento parte de geração de pdf ficha cem
def pdf(request, pessoa_id, ano):
    import io
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    contexto = buscar_informacoes_ficha(pessoa_id,ano)
   
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
   
    elements = []

    # cria informações para a primeira linha da tabela
    mes_dias = ["Mês/Dia"]
    for i in range(1,32):
        mes_dias.append(i)
    mes_dias.append('Tempos')

    # insere a chave dentro da lista dos meses na posição 0. Ex ['janeiro','C','C'...]
    for k,v in contexto['meses'].items():
        v.insert(0,k)

    

    # insere informações do contexto referentes a cada mês naquela linha
    contexto['meses']['janeiro'].append('Tempos')
    if len(contexto['meses']['fevereiro']) == 29:
       
        contexto['meses']['fevereiro'].extend(['','','','Função','Cargo','UE'])
    else:
        contexto['meses']['fevereiro'].extend(['','','Função','Cargo','UE'])
    contexto['meses']['marco'].extend(['Atribuição'])
    contexto['meses']['abril'].extend(['',contexto['funcao_at'], contexto['cargo_at'], contexto['ue_at']])
    contexto['meses']['maio'].extend(['Anterior'])
   
    contexto['meses']['junho'].extend(['',contexto['funcao_a'], contexto['cargo_a'], contexto['ue_a']])
    contexto['meses']['julho'].extend(['Atual'])
    
    contexto['meses']['agosto'].extend([contexto['funcao'], contexto['cargo'], contexto['ue']])

    # insere no dicionario faltas na posição 0 a sigla da falta Ex 'contexto['FJ']'=['FJ','FALTA JUSTIFICADA',10]
    for k,v in contexto['tp_faltas'].items():
        v.insert(0,k)
    
    # cria lista com os valores não a chave
    data_tp_falta = [tp for tp in contexto['tp_faltas'].values()]
    
    # cria lista com os valores dos meses 
    data_frequencia = [m for m in contexto['meses'].values()]

    # dentro dessa lista insere a lista mes_dias
    data_frequencia.insert(0, mes_dias)


    # cria estilo 
    style_table_corpo = TableStyle([('GRID',(0,0),(-1,-1), 0.5, colors.black),
                            ('LEFTPADDING',(0,0),(-1,-1),2),
                            ('TOPPADDING',(0,0),(-1,-1),2),
                            ('BOTTOMPADDING',(0,0),(-1,-1),2),
                            ('RIGHTPADDING',(0,0),(-1,-1),2),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('FONTSIZE',(0,0), (-1,-1),8.5), 
                            ('SPAN',(32,0),(34,1)),
                            ('SPAN',(32,3),(34,3)),
                            ('SPAN',(32,5),(34,5)),
                            ('SPAN',(32,7),(34,7)),
                            ('SPAN',(32,9),(34,12)),             
                            ])

    # cria tabela com as informações de data_faltas
    t_frequencia = Table(data_frequencia, hAlign='LEFT')
   
    # aplica estilo diferente conforme a condição, ou seja, as faltas ficam com cor de background
    for row, values in enumerate(data_frequencia):
       for column, value in enumerate(values):
        #    print(column, value)
           if value in contexto['tp_faltas']:
               style_table_corpo.add('BACKGROUND',(column,row),(column,row),colors.lightblue)

    t_frequencia.setStyle(style_table_corpo)

    t_tipos = Table(data_tp_falta, style=[('GRID',(0,0),(-1,-1), 0.5, colors.black),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('FONTSIZE',(0,0), (-1,-1),8.5),
                            ], hAlign='LEFT')

    styles = getSampleStyleSheet()
    
    styleH = ParagraphStyle('Cabeçalho',
                            fontSize=20,
                            parent=styles['Heading1'],
                            alignment=1,
                            spaceAfter=14)
    
    styleB = ParagraphStyle('Corpo',
                        spaceAfter=14
                    ) 
    styleAss = ParagraphStyle('Assinatura',
                        alignment=1
                    ) 
   
    # elements.append(Paragraph('<para><img src="https://www.orlandia.sp.gov.br/novo/wp-content/uploads/2017/01/brasaoorlandia.png" width="40" height="40"/> </para>'))
    elements.append(Paragraph(f"<strong>Ficha Frequência - Ano</strong>:{contexto['ano']}", styleH))
    # elements.append(Paragraph(f"<strong>Nome</strong>: {contexto['pessoa'].nome}  RM: {contexto['pessoa'].id}", styleB))
    
    data_pessoa = [
        [Paragraph(f"<strong>Nome: </strong>{contexto['pessoa'].nome}"),Paragraph(f"<strong>Matrícula: </strong>{contexto['pessoa'].id}"),
        Paragraph(f"<strong>Cargo: </strong>{contexto['des_cargo']}"), Paragraph(f"<strong>Disciplina: </strong>{contexto['disciplina']}")],
        [Paragraph(f"<strong>CPF: </strong>{contexto['pessoa'].cpf}"),Paragraph(f"<strong>Data de Admissão: </strong>{contexto['pessoa'].admissao}"),
        Paragraph(f"<strong>Efetivo: </strong>{contexto['pessoa'].efetivo}")]
    ]
    tb_pessoa = Table(data_pessoa,style=[('GRID',(0,0),(-1,-1), 0.5, colors.white),
                                ('ALIGN',(0,0),(-1,-1),'LEFT'),
                            ('FONTSIZE',(0,0), (-1,-1),8.5),
                            ],hAlign='LEFT')
    
    #Send the data and build the file
    elements.append(tb_pessoa)
    elements.append(t_frequencia)

    elements.append(Paragraph(f"", styleB))
    elements.append(t_tipos)

    elements.append(Paragraph('____________________________', styleAss))
    elements.append(Paragraph('Nome', styleAss))
    elements.append(Paragraph('RG:11.111.111',styleAss))
    elements.append(Paragraph('Diretora',styleAss))

    doc.build(elements)
    nome_arquivo = str(contexto["pessoa"].nome).replace(' ','_') + datetime.strftime(datetime.now(),'_%d/%m/%Y_%H_%M_%S')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={nome_arquivo}.pdf'
    response.write(buffer.getvalue())
    buffer.close()

    return response

def pdf_v2(request, pessoa_id, ano):
    import io
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    contexto = buscar_informacoes_ficha(pessoa_id,ano)
   
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
   
    elements = []

    # cria informações para a primeira linha da tabela
    mes_dias = ["Mês/Dia"]
    for i in range(1,32):
        mes_dias.append(i)
    # mes_dias.append('Tempos')

    # insere a chave dentro da lista dos meses na posição 0. Ex ['janeiro','C','C'...]
    for k,v in contexto['meses'].items():
        v.insert(0,k)

    # insere no dicionario faltas na posição 0 a sigla da falta Ex 'contexto['FJ']'=['FJ','FALTA JUSTIFICADA',10]
    for k,v in contexto['tp_faltas'].items():
        v.insert(0,k)

    # cria lista com os valores não a chave
    data_tp_falta = [tp for tp in contexto['tp_faltas'].values()]
    
    # cria lista com os valores dos meses 
    data_frequencia = [m for m in contexto['meses'].values()]

    # dentro dessa lista insere a lista mes_dias
    data_frequencia.insert(0, mes_dias)

    faltas_mes_a_mes = contexto['falta_por_mes']
    linha = 0
    eventos_por_mes = []
    intermediaria = []
    
    for k in faltas_mes_a_mes:
        linha +=1
        if k in ['janeiro','marco','maio','julho','agosto','outubro','dezembro']:
            eventos_por_mes.append(list(faltas_mes_a_mes[k].values()))
        elif k in ['abril','junho','setembro','novembro']:
            intermediaria = list(faltas_mes_a_mes[k].values())
            # intermediaria.insert(0,' ')
            eventos_por_mes.append(intermediaria)
        else:
            intermediaria = list(faltas_mes_a_mes[k].values())
            # if bissexto(ano):
            #     for i in range(2):
            #         intermediaria.insert(0,' ')
            # else:
            #     for i in range(3):
            #         intermediaria.insert(0,' ')
            eventos_por_mes.append(intermediaria)

    # pega chaves de um mes qualquer que será a linha de eventos
    eventos_por_mes.insert(0,list(contexto['falta_por_mes']['janeiro'].keys()))
    
    # extend a tabela frequencia com informação dos eventos
    for i in range(0,len(data_frequencia)):
        data_frequencia[i].extend(eventos_por_mes[i])
    
    data_frequencia[0].extend(['Tempos'])
    data_frequencia[3].extend(['Cargo','Função','UE'])
  
    data_frequencia[5].extend(['Atribuição'])
    data_frequencia[6].extend([contexto['cargo_at'], contexto['funcao_at'], contexto['ue_at']])
    data_frequencia[7].extend(['Anterior'])
    data_frequencia[8].extend([contexto['cargo_a'], contexto['funcao_a'], contexto['ue_a']])
    data_frequencia[9].extend(['Atual'])
    data_frequencia[10].extend([contexto['cargo'], contexto['funcao'], contexto['ue']])

   
    # cria estilo 
    style_table_corpo = TableStyle([('GRID',(0,0),(-1,-1), 0.5, colors.black),
                            ('LEFTPADDING',(0,0),(-1,-1),2),
                            ('TOPPADDING',(0,0),(-1,-1),2),
                            ('BOTTOMPADDING',(0,0),(-1,-1),2),
                            ('RIGHTPADDING',(0,0),(-1,-1),2),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('FONTSIZE',(0,0), (-1,-1),8.5), 
                            ('SPAN',(-3,-13),(-1,-12)),
                            ('SPAN',(-3,-8),(-1,-8)),
                            ('SPAN',(-3,-6),(-1,-6)),
                            ('SPAN',(-3,-4),(-1,-4)),
                            ('BOX',(-3,-13),(-1,-1),2,colors.black),
                            ('BOX',(32,0),(-1,-1),2,colors.black),
                            ('BACKGROUND',(32,0),(-4,-1),colors.antiquewhite),
                            ('BOX',(0,0),(32,13),2,colors.black)             
                            ], spaceBefore=20)

    # cria tabela com as informações de data_faltas
    t_frequencia = Table(data_frequencia, hAlign='CENTER',)

    
    # aplica estilo diferente conforme a condição, ou seja, as faltas ficam com cor de background
    for row, values in enumerate(data_frequencia):
       for column, value in enumerate(values):
        #    print(column, value)
           if value in contexto['tp_faltas']:
               style_table_corpo.add('BACKGROUND',(column,row),(column,row),colors.lightblue)

    t_frequencia.setStyle(style_table_corpo)

    t_tipos = Table(data_tp_falta, style=[('GRID',(0,0),(-1,-1), 0.5, colors.black),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('FONTSIZE',(0,0), (-1,-1),7.5),
                            ('LEFTPADDING',(0,0),(-1,-1),1),
                            ('TOPPADDING',(0,0),(-1,-1),1),
                            ('BOTTOMPADDING',(0,0),(-1,-1),1),
                            ('RIGHTPADDING',(0,0),(-1,-1),1),
                            ], hAlign='LEFT')

    styles = getSampleStyleSheet()
    
    styleH = ParagraphStyle('Cabeçalho',
                            fontSize=20,
                            parent=styles['Heading1'],
                            alignment=1,
                            spaceAfter=14)
    
    styleB = ParagraphStyle('Corpo',
                        spaceAfter=14
                    ) 
    styleAss = ParagraphStyle('Assinatura',
                        alignment=1,
            
                    ) 

    styleAssTrac =  ParagraphStyle('AssinaturaTrac',
                        alignment=1,
                        spaceBefore=20
            
                    ) 

    stylePessoa = ParagraphStyle('Pessoa',
                        # alignment=0,
                        spaceAfter=4
                        
                    ) 
   
    # elements.append(Paragraph('<para><img src="https://www.orlandia.sp.gov.br/novo/wp-content/uploads/2017/01/brasaoorlandia.png" width="40" height="40"/> </para>'))
    elements.append(Paragraph(f"<strong>Ficha Frequência - Ano</strong>:{contexto['ano']}", styleH))
    # elements.append(Paragraph(f"<strong>Nome</strong>: {contexto['pessoa'].nome}  RM: {contexto['pessoa'].id}", styleB))
    
    data_pessoa = [
        [Paragraph(f"<strong>Nome: </strong>{contexto['pessoa'].nome}",stylePessoa),Paragraph(f"<strong>Matrícula: </strong>{contexto['pessoa'].id}", stylePessoa),
        Paragraph(f"<strong>Cargo: </strong>{contexto['des_cargo']}", stylePessoa), Paragraph(f"<strong>Disciplina: </strong>{contexto['disciplina']}", stylePessoa)],
        [Paragraph(f"<strong>CPF: </strong>{contexto['pessoa'].cpf}", stylePessoa),Paragraph(f"<strong>Data de Admissão: </strong>{contexto['pessoa'].admissao}", stylePessoa),
        Paragraph(f"<strong>Efetivo: </strong>{contexto['pessoa'].efetivo}", stylePessoa)]
    ]

   

    tb_pessoa = Table(data_pessoa,style=([('GRID',(0,0),(-1,-1), 0.5, colors.white),
                            ('LEFTPADDING',(0,0),(-1,-1),2),
                            ('TOPPADDING',(0,0),(-1,-1),2),
                            ('BOTTOMPADDING',(0,0),(-1,-1),2),
                            ('RIGHTPADDING',(0,0),(-1,-1),0),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                                      
                            ]), hAlign='CENTER')
    #Send the data and build the file
    elements.append(tb_pessoa)
    elements.append(t_frequencia)

    elements.append(Paragraph(f"", styleB))
    

    elements.append(Paragraph('____________________________', styleAssTrac))
    elements.append(Paragraph('Nome', styleAss))
    elements.append(Paragraph('RG:11.111.111',styleAss))
    elements.append(Paragraph('Diretora',styleAss))
    
    elements.append(t_tipos)
    doc.build(elements)
    nome_arquivo = str(contexto["pessoa"].nome).replace(' ','_') + datetime.strftime(datetime.now(),'_%d/%m/%Y_%H_%M_%S')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={nome_arquivo}.pdf'
    response.write(buffer.getvalue())
    buffer.close()

    return response

def pdf_v3(request, pessoa_id, ano):
    import io
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    contexto = buscar_informacoes_ficha_v2(pessoa_id,ano)
   
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
   
    elements = []

    # cria informações para a primeira linha da tabela
    mes_dias = ["Mês/Dia"]
    for i in range(1,32):
        mes_dias.append(i)
    # mes_dias.append('Tempos')

    # insere a chave dentro da lista dos meses na posição 0. Ex ['janeiro','C','C'...]
    for k,v in contexto['meses'].items():
        v.insert(0,k)

    # insere no dicionario faltas na posição 0 a sigla da falta Ex 'contexto['FJ']'=['FJ','FALTA JUSTIFICADA',10]
    for k,v in contexto['tp_faltas'].items():
        v.insert(0,k)

    # cria lista com os valores não a chave
    data_tp_falta = [tp for tp in contexto['tp_faltas'].values()]
    
    # cria lista com os valores dos meses 
    data_frequencia = [m for m in contexto['meses'].values()]

    # dentro dessa lista insere a lista mes_dias
    data_frequencia.insert(0, mes_dias)

    faltas_mes_a_mes = contexto['falta_por_mes']
    linha = 0
    eventos_por_mes = []
    intermediaria = []
    
    for k in faltas_mes_a_mes:
        linha +=1
        if k in ['janeiro','marco','maio','julho','agosto','outubro','dezembro']:
            eventos_por_mes.append(list(faltas_mes_a_mes[k].values()))
        elif k in ['abril','junho','setembro','novembro']:
            intermediaria = list(faltas_mes_a_mes[k].values())
            eventos_por_mes.append(intermediaria)
        else:
            intermediaria = list(faltas_mes_a_mes[k].values())
            eventos_por_mes.append(intermediaria)

    # pega chaves de um mes qualquer que será a linha de eventos
    eventos_por_mes.insert(0,list(contexto['falta_por_mes']['janeiro'].keys()))
    
    # extend a tabela frequencia com informação dos eventos
    for i in range(0,len(data_frequencia)):
        data_frequencia[i].extend(eventos_por_mes[i])
    
    linha = []
    linha2 = []
    brancos = 0
    brancos = len(contexto['tp_faltas'])
    brancos += 33
    for i in range(brancos):
        linha.append(' ')
    data_frequencia.insert(1,linha)

    for i in range(brancos):
        linha2.append(' ')
    data_frequencia.insert(0,linha2)

    data_frequencia[0].extend(['Tempos'])
    data_frequencia[1].extend(['Função','Cargo','Unidade'])
    data_frequencia[2].extend([contexto['funcao_a'],contexto['cargo_a'],contexto['ue_a']])
    
    funcao_anual = []
    cargo_anual = []
    ue_anual = []
    for v in contexto['cargo'].values():
        cargo_anual.append(v)
    for v in contexto['funcao'].values():
        funcao_anual.append(v)
    for v in contexto['ue'].values():
        ue_anual.append(v)

    # data_frequencia.extend(cargo)
    print(cargo_anual,funcao_anual,ue_anual)
    inicio_linha = 3
    for i in range(12):
        data_frequencia[inicio_linha].extend([funcao_anual[i],cargo_anual[i],ue_anual[i]])
        inicio_linha += 1
    # print("Cargo",contexto['cargo'],"Funcao",contexto['funcao'],'UE',contexto['ue'])
   
    # data_frequencia[5].extend(['Atribuição'])
    # data_frequencia[6].extend([contexto['cargo_at'], contexto['funcao_at'], contexto['ue_at']])
    # data_frequencia[7].extend(['Anterior'])
    # data_frequencia[8].extend([contexto['cargo_a'], contexto['funcao_a'], contexto['ue_a']])
    # data_frequencia[9].extend(['Atual'])
    # data_frequencia[10].extend([contexto['cargo'], contexto['funcao'], contexto['ue']])

   
    
   

    # cria estilo 
    style_table_corpo = TableStyle([('GRID',(0,0),(-1,-1), 0.5, colors.black),
                            ('LEFTPADDING',(0,0),(-1,-1),2),
                            ('TOPPADDING',(0,0),(-1,-1),2),
                            ('BOTTOMPADDING',(0,0),(-1,-1),2),
                            ('RIGHTPADDING',(0,0),(-1,-1),2),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('FONTSIZE',(0,0), (-1,-1),8.5), 
                            # ('SPAN',(-3,-13),(-1,-12)),
                            # ('SPAN',(-3,-8),(-1,-8)),
                            # ('SPAN',(-3,-6),(-1,-6)),
                            # ('SPAN',(-3,-4),(-1,-4)),
                            # ('BOX',(-3,-13),(-1,-1),2,colors.black),
                            # ('BOX',(32,0),(-1,-1),2,colors.black),
                            # ('BACKGROUND',(32,0),(-4,-1),colors.antiquewhite),
                            # ('BOX',(0,0),(32,13),2,colors.black)             
                            ], spaceBefore=20)

    # cria tabela com as informações de data_faltas
    t_frequencia = Table(data_frequencia, hAlign='CENTER',)

    
    # aplica estilo diferente conforme a condição, ou seja, as faltas ficam com cor de background
    for row, values in enumerate(data_frequencia):
       for column, value in enumerate(values):
        #    print(column, value)
           if value in contexto['tp_faltas']:
               style_table_corpo.add('BACKGROUND',(column,row),(column,row),colors.lightblue)

    t_frequencia.setStyle(style_table_corpo)

    t_tipos = Table(data_tp_falta, style=[('GRID',(0,0),(-1,-1), 0.5, colors.black),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('FONTSIZE',(0,0), (-1,-1),7.5),
                            ('LEFTPADDING',(0,0),(-1,-1),1),
                            ('TOPPADDING',(0,0),(-1,-1),1),
                            ('BOTTOMPADDING',(0,0),(-1,-1),1),
                            ('RIGHTPADDING',(0,0),(-1,-1),1),
                            ], hAlign='LEFT')

    styles = getSampleStyleSheet()
    
    styleH = ParagraphStyle('Cabeçalho',
                            fontSize=20,
                            parent=styles['Heading1'],
                            alignment=1,
                            spaceAfter=14)
    
    styleB = ParagraphStyle('Corpo',
                        spaceAfter=14
                    ) 
    styleAss = ParagraphStyle('Assinatura',
                        alignment=1,
            
                    ) 

    styleAssTrac =  ParagraphStyle('AssinaturaTrac',
                        alignment=1,
                        spaceBefore=20
            
                    ) 

    stylePessoa = ParagraphStyle('Pessoa',
                        # alignment=0,
                        spaceAfter=4
                        
                    ) 
   
    # elements.append(Paragraph('<para><img src="https://www.orlandia.sp.gov.br/novo/wp-content/uploads/2017/01/brasaoorlandia.png" width="40" height="40"/> </para>'))
    elements.append(Paragraph(f"<strong>Ficha Frequência - Ano</strong>:{contexto['ano']}", styleH))
    # elements.append(Paragraph(f"<strong>Nome</strong>: {contexto['pessoa'].nome}  RM: {contexto['pessoa'].id}", styleB))
    
  
    
    saida = '' if contexto['pessoa'].saida == None else  contexto['pessoa'].saida.strftime('%d/%m/%Y')

    data_pessoa = [
        [Paragraph(f"<strong>Nome: </strong>{contexto['pessoa'].nome}",stylePessoa),Paragraph(f"<strong>Matrícula: </strong>{contexto['pessoa'].id}", stylePessoa),
        Paragraph(f"<strong>Cargo: </strong>{contexto['des_cargo']}", stylePessoa), Paragraph(f"<strong>Disciplina: </strong>{contexto['disciplina']}", stylePessoa)],
        [Paragraph(f"<strong>CPF: </strong>{contexto['pessoa'].cpf}", stylePessoa),Paragraph(f"<strong>Data de Admissão: </strong>{contexto['pessoa'].admissao.strftime('%d/%m/%Y')}", stylePessoa),
        Paragraph(f"<strong>Data de Saída: </strong>{saida}", stylePessoa),
        Paragraph(f"<strong>Efetivo: </strong>{contexto['pessoa'].efetivo}", stylePessoa)]
    ]

    tb_pessoa = Table(data_pessoa,style=([('GRID',(0,0),(-1,-1), 0.5, colors.white),
                            ('LEFTPADDING',(0,0),(-1,-1),2),
                            ('TOPPADDING',(0,0),(-1,-1),2),
                            ('BOTTOMPADDING',(0,0),(-1,-1),2),
                            ('RIGHTPADDING',(0,0),(-1,-1),0),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ]), hAlign='CENTER')

    #Send the data and build the file
    elements.append(tb_pessoa)
    elements.append(t_frequencia)

    elements.append(Paragraph(f"", styleB))
    
    elements.append(Paragraph('____________________________', styleAssTrac))
    elements.append(Paragraph('Nome', styleAss))
    elements.append(Paragraph('RG:11.111.111',styleAss))
    elements.append(Paragraph('Diretora',styleAss))
    
    elements.append(t_tipos)
    doc.build(elements)
    nome_arquivo = str(contexto["pessoa"].nome).replace(' ','_') + datetime.strftime(datetime.now(),'_%d/%m/%Y_%H_%M_%S')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={nome_arquivo}.pdf'
    response.write(buffer.getvalue())
    buffer.close()

    return response

def atualizar_pontuacoes(request, pontuacao_id, pessoa_id):

    pontuacao = Pontuacoes.objects.get(pk=pontuacao_id)
    pontuacoes = Pontuacoes.objects.all().filter(pessoa=pessoa_id)
    pessoa = Pessoas.objects.get(pk=pessoa_id)

    if request.method == 'POST':
        form = formularioPontuacao(request.POST, instance=pontuacao)
        
        if form.is_valid():
           
            form.save()
            
            messages.success(request,"Pontuação Gravada!")
            return redirect('lancarpontuacao',pessoa_id)
        else:
            messages.error(request,"Erro ao  Gravar Pontuação!",'danger')
            

    else:
        form = formularioPontuacao(instance=pontuacao,initial={'pessoa':pessoa})
    
    return render(request,'template/lancar_pontuacao.html',{'form':form,'pessoa':pessoa,'pontuacoes':pontuacoes})

def consultar_anos_status(pessoa):
    anos, pessoa = listar_anos(pessoa)
    
    anos_status = {}
   
    for a in anos:
        status  = checar_existencia_pontuacao(a,pessoa)
        if status:
            status = 'Aberto'
        else:
            status = 'Fechado'
        anos_status[a] = status

    return anos_status,anos

def encerrar_ano_v2(request, pessoa_id, ano):
    
    q1 = Pontuacoes.objects.all().filter(pessoa=pessoa_id).filter(ano=ano)
    q2= Pontuacoes.objects.all().filter(pessoa=pessoa_id).filter(ano=ano-1)

    pessoa = Pessoas.objects.get(pk=pessoa_id)
    dicionario =   gerar_pontuacao_anual_v2(ano,pessoa)
   
    funcao = dicionario[0]['dezembro']
    cargo = dicionario[1]['dezembro']
    ue = dicionario[2]['dezembro']

    # anos, pessoa = listar_anos(pessoa.id)
    anos_status, anos = consultar_anos_status(pessoa.id)
    min_ano = min(anos)
    max_ano = max(anos)

    template = ''
    if 'encerrar' in request.get_full_path():
        template = 'ficha'
        argumento = ano
    else:
        template = 'listarficha'
        argumento = pessoa_id
    # anos_status = {}
   
    # for a in anos:
    #     status  = checar_existencia_pontuacao(a,pessoa)
    #     if status:
    #         status = 'Aberto'
    #     else:
    #         status = 'Fechado'
    #     anos_status[a] = status
    
   
    if request.method == 'GET':

        if  q1.count() == 0 and  min_ano == ano and pessoa.efetivo == True:
            pontuacao = Pontuacoes(ano=ano,funcao=funcao,cargo=cargo,ue=ue,pessoa=pessoa)
            pontuacao.save()

            messages.success(request,f"Ano {ano} fechado com sucesso!")
        
        elif q2.count() != 0 :
            pontuacao = Pontuacoes(ano=ano,funcao=funcao,cargo=cargo,ue=ue,pessoa=pessoa)
            pontuacao.save()
            
            messages.success(request,f"Ano {ano} fechado com sucesso!")
            
        elif q1.count() == 0 and pessoa.efetivo == False:
            pontuacao = Pontuacoes(ano=ano,funcao=funcao,cargo=cargo,ue=ue,pessoa=pessoa)
            pontuacao.save()
            
            messages.success(request,f"Ano {ano} fechado com sucesso!") 

        else:
            messages.info(request,f"Ano anterior {ano - 1} aberto!")

        print(request.META)
        return redirect('listarficha',pessoa_id)
       
        # return redirect('encerrarano',pessoa_id,ano)     

    return render(request,'template/listar_ficha.html',{'anos':anos_status, 'pessoa':pessoa})

def encerrar_ano(request, pessoa_id, ano):
    
    q1 = Pontuacoes.objects.all().filter(pessoa=pessoa_id).filter(ano=ano)
    q2= Pontuacoes.objects.all().filter(pessoa=pessoa_id).filter(ano=ano-1)

    pessoa = Pessoas.objects.get(pk=pessoa_id)
    cargo, funcao, ue =   gerar_pontuacao_anual(ano,pessoa)
    cargo_a, funcao_a, ue_a =   gerar_pontuacao_anual(ano,pessoa,'a')
    cargo_at, funcao_at, ue_at = gerar_pontuacao_atribuicao(ano, pessoa)
    soma_a = cargo_a + funcao_a + ue_a
    anos, pessoa = listar_anos(pessoa.id)
    min_ano = min(anos)
    max_ano = max(anos)

    anos_status = {}
   
    for a in anos:
        status  = checar_existencia_pontuacao(a,pessoa)
        if status:
            status = 'Aberto'
        else:
            status = 'Fechado'
        anos_status[a] = status
    
   
    if request.method == 'GET':

        if  q1.count() == 0 and  min_ano == ano and pessoa.efetivo == True:
            pontuacao = Pontuacoes(ano=ano,cargo=cargo,funcao=funcao,ue=ue,pessoa=pessoa, 
            cargo_atrib=cargo_at, funcao_atrib=funcao_at,ue_atrib=ue_at)
            pontuacao.save()

            messages.success(request,f"Ano {ano} fechado com sucesso!")
        
        elif q2.count() != 0 :
            pontuacao = Pontuacoes(ano=ano,cargo=cargo,funcao=funcao,ue=ue,pessoa=pessoa, 
            cargo_atrib=cargo_at, funcao_atrib=funcao_at,ue_atrib=ue_at)
            pontuacao.save()
            
            messages.success(request,f"Ano {ano} fechado com sucesso!")
            
        elif q1.count() == 0 and pessoa.efetivo == False:
            pontuacao = Pontuacoes(ano=ano,cargo=cargo,funcao=funcao,ue=ue,pessoa=pessoa, 
            cargo_atrib=cargo_at, funcao_atrib=funcao_at,ue_atrib=ue_at)
            pontuacao.save()
            
            messages.success(request,f"Ano {ano} fechado com sucesso!") 

        else:
            messages.info(request,f"Ano anterior {ano - 1} aberto!")

        
        return redirect('listarficha',pessoa_id)     

       
    return render(request,'template/listar_ficha.html',{'anos':anos_status, 'pessoa':pessoa})

def abrir_ano(request, pessoa_id, ano):

    pessoa = Pessoas.objects.get(pk=pessoa_id)
    # anos, pessoa = listar_anos(pessoa_id)
    anos_status, anos = consultar_anos_status(pessoa.id)
    abrir_todos = False
    q2= Pontuacoes.objects.all().filter(pessoa=pessoa_id).filter(ano=ano+1)
    min_ano = min(anos)
    max_ano = max(anos)

    if ano == min_ano:
        abrir_todos = True

    # anos_status = {}
   
    # for a in anos:
    #     status  = checar_existencia_pontuacao(a,pessoa)
    #     if status:
    #         status = 'Aberto'
    #     else:
    #         status = 'Fechado'
    #     anos_status[a] = status

    
    if request.method == 'GET':
        
        if abrir_todos and pessoa.efetivo:
            for i in anos:
                
                q1 = Pontuacoes.objects.all().filter(pessoa=pessoa_id).filter(ano=i)
                q1.delete() 
                 
            messages.success(request,f"Aberto do ano {min_ano} ao {max_ano}")
        else:
            if q2.count() > 0 and pessoa.efetivo:
                messages.info(request,f"Não pode abrir {ano} existe ano posterior Fechado!")
            else:
                q1 = Pontuacoes.objects.all().filter(pessoa=pessoa_id).filter(ano=ano)
                q1.delete()    
                messages.success(request,f"Ano {ano} Aberto!")
          
        return redirect('listarficha',pessoa_id)     
   

    
    return render(request,'template/listar_ficha.html',{'anos':anos_status, 'pessoa':pessoa})

def excluir_pontuacoes(request, pessoa_id, pontuacao_id):
    pontuacao = Pontuacoes.objects.get(pk=pontuacao_id)
    pontuacoes = Pontuacoes.objects.all().filter(pessoa=pessoa_id).order_by('ano')
    pessoa = Pessoas.objects.get(pk=pessoa_id)

    if request.method == 'GET':
        pontuacao.delete()    
        messages.success(request,"Pontuação Apagada!")
        return redirect('lancarpontuacao',pessoa_id)     
    else:
        form = formularioPontuacao(initial={'pessoa':pessoa})
    
    return render(request,'template/lancar_pontuacao.html',{'form':form,'pessoa':pessoa,'pontuacoes':pontuacoes})

def lancar_pontuacoes(request, pessoa_id):

    pessoa = Pessoas.objects.get(pk=pessoa_id)
    pontuacoes = Pontuacoes.objects.filter(pessoa=pessoa_id).order_by('ano')
    
    if request.method == 'POST':
        form = formularioPontuacao(request.POST)
        ano = form['ano'].value()
        if pessoa.admissao.year <= int(ano) and int(ano) <= pessoa.saida.year :
            if form.is_valid():
            
                form.save()
                messages.success(request,"Pontuação Gravada!")
                return redirect('lancarpontuacao',pessoa_id)
            else:
                messages.error(request,"Erro ao  Gravar Pontuação!",'danger')
        else:
            messages.error(request,f"Erro ao  Gravar Pontuação! Ano Admissao: {pessoa.admissao.year} Ano Saída: {pessoa.saida.year}",'danger')


    else:
        form = formularioPontuacao(initial={'pessoa':pessoa})
        
    
    
    return render(request,'template/lancar_pontuacao.html',{'form':form,'pessoa':pessoa,'pontuacoes':pontuacoes})


# dado um determinado ano acumula dias por meses
def acumular_dias(ano,pessoa_id,acumulado=0):
    meses = configurar_meses_v4(ano,pessoa_id)
    
    dias_acumulados_por_mes = {}
    # for k in meses.keys():
    #     mes = retornar_mes_num(k)      
    #     acumulo += mes[1]
    #     dicio_acumulo[k] = acumulo
    dias = 0
    for k,v in meses.items():
        for d in v:
            if d != '-':
                dias += 1
        acumulado += dias
        if k == 'outubro':
            acumulado -=  faltas_a_descontar(ano,pessoa_id)
            dias_acumulados_por_mes[k] = acumulado 
        else:
            dias_acumulados_por_mes[k] = acumulado
        dias = 0
    
   
    return dias_acumulados_por_mes


def coletivo(request):

    return render(request,'template/coletivo.html')

def lancar_evento_coletivo(request):
    pessoas = Pessoas.objects.all()
   
    if request.method == 'POST':

        # instância do formulário para pegar dados
        form = formularioLF(request.POST)
        
        # pegar valores do formulário
        qtd_dias = int(form.data['qtd_dias'])
        data_lancamento = form['data'].value()
        falta = Faltas.objects.get(pk=form['falta'].value())

        data_lancamento = datetime.strptime(data_lancamento, '%Y-%m-%d').date()

        # criar intervalos de lançamentos na memória e dividir por ano (ano é chave)
        dia_mes_ano = gerar_lancamento_em_memoria(data_lancamento,qtd_dias)
        log_id = []
        # verifica se os dados preenchidos são válidos
        # verifica se existe faltas naquele intervalo
        for pessoa in pessoas:
            conflito, ano_fechado = lancar_falta(data_lancamento, qtd_dias ,pessoa.id)
            if data_lancamento > pessoa.admissao:
                
                if conflito:
                    if not ano_fechado:
                        # navega entre as chaves (ano)
                        for k in dia_mes_ano.keys():
                            qtd_dias = len(dia_mes_ano[k]) # quantos dias existem dentro da chave ano
                            data_lancamento = dia_mes_ano[k][0] # pega o primeiro dia do lançamento e depois o primeiro dia do ano

                            # cria objeto com os novos dados
                            novoObj = Faltas_Pessoas(pessoa=pessoa,data=data_lancamento,qtd_dias=qtd_dias,falta=falta)
                            
                            # salva o objeto
                            novoObj.save()
                            
                            messages.success(request,f"Evento Coletivo registrado! {pessoa.nome}")

                    else:
                        messages.error(request,f"Ano {data_lancamento.year} Fechado! Abrir se deseja efetuar lançamentos!",'danger')

                else:
                    messages.error(request,"Não foi possível registrar a falta! Pode existir conflito de datas!",'danger')

    form = formularioLF()

    return render(request,'template/lancar_evento_coletivo.html', {'form':form})
