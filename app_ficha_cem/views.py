from django.shortcuts import render, redirect
from .models import Faltas, Pessoas, Faltas_Pessoas, Pontuacoes, PontuacoesAtribuicoes, Cargos
from .forms import formularioPessoa, formularioTF, formularioLF, formularioCargo
from django.views import View
from django.contrib import messages
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

# faz a pesquisa e incremento para verificar se existe falta lançada naquela data, impedindo lançamento em data
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
  
    return render(request,'template/listar_ficha.html',{'anos':anos_status, 'pessoa':pessoa})

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

def cargos(request):
    cargos = Cargos.objects.all()
    if request.method == 'POST':
        form = formularioCargo(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listarcargos')
    else:
        form = formularioCargo()
    return render(request,'template/cadastrar_cargo.html',{'form':form, 'cargos':cargos})

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

def buscar_informacoes_ficha(pessoa_id, ano):
    anos, pessoa = listar_anos(pessoa_id)
    pessoa = Pessoas.objects.get(pk=pessoa_id)
    print('descontar',faltas_a_descontar(ano, pessoa))
    # meses = configurar_meses(ano)
    meses = configurar_meses_v2(ano,pessoa_id)
    cargo, funcao, ue  = gerar_pontuacao_anual(ano,pessoa)
    cargo_a, funcao_a, ue_a  = gerar_pontuacao_anual(ano,pessoa,'a')
    cargo_at, funcao_at, ue_at = gerar_pontuacao_atribuicao(ano, pessoa)
    dias = range(1,32)
    faltas = Faltas_Pessoas.objects.all().order_by('data').filter(data__year=ano).filter(pessoa=pessoa_id)
    admissao = pessoa.admissao
    dia_adm= pessoa.admissao.day
    mes_adm = pessoa.admissao.month
    ano_adm = pessoa.admissao.year

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

    cargo, disciplina = cargo_disciplina
 
    tipo_faltas=contar_tipos_faltas(faltas)
    print(tipo_faltas)
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

    pessoa.cpf = f'{pessoa.cpf[:3]}.{pessoa.cpf[3:6]}.{pessoa.cpf[6:9]}-{pessoa.cpf[-2:]}'
    pessoa.admissao = f'{dia_adm}/{mes_adm}/{ano_adm}'
    print(pessoa.efetivo)
    if pessoa.efetivo:
        pessoa.efetivo='Sim'
    else:
        pessoa.efetivo='Não'

    contexto = {
        'meses': meses,
        'ano': ano,
        'funcao': funcao,
        'cargo': cargo,
        'disciplina': disciplina,
        'ue': ue,
        'funcao_a': funcao_a,
        'cargo_a': cargo_a,
        'ue_a': ue_a,
        'funcao_at':funcao_at,
        'cargo_at': cargo_at,
        'ue_at': ue_at,
        'nome': pessoa.nome,
        'pessoa': pessoa,
        'dias': dias,
        'tp_faltas': tipo_faltas,
        'admissao':admissao,
        'anos':anos
        # 'pagesize':'A4'

    }

    return contexto

def gerar_ficha(request, pessoa_id, ano):
    
    contexto = buscar_informacoes_ficha(pessoa_id, ano)
    
    return render(request,'template/ficha_cem.html', {'contexto':contexto})

def index(request):
    return render(request,'template/index.html')

def encerrar_ano(request, pessoa_id, ano):

    pessoa = Pessoas.objects.get(pk=pessoa_id)
    cargo, funcao, ue =   gerar_pontuacao_anual(ano,pessoa)
    cargo_a, funcao_a, ue_a =   gerar_pontuacao_anual(ano,pessoa,'a')
    cargo_at, funcao_at, ue_at = gerar_pontuacao_atribuicao(ano, pessoa)
    soma_a = cargo_a + funcao_a + ue_a
    anos, pessoa = listar_anos(pessoa.id)
    
    try:
        if anos.index(ano) == 0 and soma_a == 0:
            pontuacao = Pontuacoes(ano=ano,cargo=cargo,funcao=funcao,ue=ue,pessoa=pessoa)
            pontuacao.save()
            pontuacao_at = PontuacoesAtribuicoes(ano=ano,cargo=cargo_at,funcao=funcao_at,ue=ue_at,pessoa=pessoa)
            pontuacao_at.save()
            messages.success(request,f"Ano {ano} fechado com sucesso!")
        else: 
            if soma_a != 0:
                pontuacao = Pontuacoes(ano=ano,cargo=cargo,funcao=funcao,ue=ue,pessoa=pessoa)
                pontuacao_at = PontuacoesAtribuicoes(ano=ano,cargo=cargo_at,funcao=funcao_at,ue=ue_at,pessoa=pessoa)
                pontuacao.save()
                pontuacao_at.save()
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
    
    q1 = PontuacoesAtribuicoes.objects.filter(ano=ano-1) # ano anterior
    q2 = PontuacoesAtribuicoes.objects.filter(pessoa=pessoa)

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
            cargo = dias -faltas_a_descontar(ano,pessoa)
            funcao = dias - faltas_a_descontar(ano,pessoa)
            ue = dias - faltas_a_descontar(ano,pessoa)
        else:
            cargo = int(pontuacao_anterior[0].cargo) + dias - faltas_a_descontar(ano,pessoa)
            funcao = int(pontuacao_anterior[0].funcao) + dias - faltas_a_descontar(ano,pessoa)
            ue = int(pontuacao_anterior[0].ue) + dias - faltas_a_descontar(ano,pessoa)
             
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
        if len(pontuacao_anterior) == 0 :
            cargo = dias
            funcao = dias
            ue = dias
        else:
            cargo = int(pontuacao_anterior[0].cargo) + dias
            funcao = int(pontuacao_anterior[0].funcao) + dias
            ue = int(pontuacao_anterior[0].ue) + dias
             
    return cargo, funcao, ue

#em desenvolvimento parte de geração de pdf ficha cem
def pdf(request, pessoa_id, ano):

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    contexto = buscar_informacoes_ficha(pessoa_id,ano)
   
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
   
    elements = []

    mes_dias = ["Mês/Dia"]
    for i in range(1,32):
        mes_dias.append(i)

    mes_dias.append('Tempos')

    for k,v in contexto['meses'].items():
        v.insert(0,k)

    print(len(contexto['meses']['fevereiro']))
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

    for k,v in contexto['tp_faltas'].items():
        v.insert(0,k)

    data_tp_falta = [tp for tp in contexto['tp_faltas'].values()]
    
    data_faltas = [m for m in contexto['meses'].values()]

    data_faltas.insert(0, mes_dias)

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

    t_faltas = Table(data_faltas, hAlign='LEFT')
   
    # aplica estilo diferente conforme a condição, ou seja, as falas ficam com cor de background
    for row, values in enumerate(data_faltas):
       for column, value in enumerate(values):
        #    print(column, value)
           if value in contexto['tp_faltas']:
               style_table_corpo.add('BACKGROUND',(column,row),(column,row),colors.lightblue)

    t_faltas.setStyle(style_table_corpo)

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
    elements.append(Paragraph(f"<strong>Ficha Cem - Ano</strong>:{contexto['ano']}", styleH))
    # elements.append(Paragraph(f"<strong>Nome</strong>: {contexto['pessoa'].nome}  RM: {contexto['pessoa'].id}", styleB))
    
    data_pessoa = [
        [Paragraph(f"<strong>Nome: </strong>{contexto['pessoa'].nome}"),Paragraph(f"<strong>Matrícula: </strong>{contexto['pessoa'].id}"),
        Paragraph(f"<strong>Cargo: </strong>{contexto['cargo']}"), Paragraph(f"<strong>Disciplina: </strong>{contexto['disciplina']}")],
        [Paragraph(f"<strong>CPF: </strong>{contexto['pessoa'].cpf}"),Paragraph(f"<strong>Data de Admissão: </strong>{contexto['pessoa'].admissao}"),
        Paragraph(f"<strong>Efetivo: </strong>{contexto['pessoa'].efetivo}")]
    ]
    tb_pessoa = Table(data_pessoa,style=[('GRID',(0,0),(-1,-1), 0.5, colors.white),
                                ('ALIGN',(0,0),(-1,-1),'LEFT'),
                            ('FONTSIZE',(0,0), (-1,-1),8.5),
                            ],hAlign='LEFT')
    
    #Send the data and build the file
    elements.append(tb_pessoa)
    elements.append(t_faltas)

    elements.append(Paragraph(f"", styleB))
    elements.append(t_tipos)

    elements.append(Paragraph('____________________________', styleAss))
    elements.append(Paragraph('Nome', styleAss))
    elements.append(Paragraph('RG:11.111.111',styleAss))
    elements.append(Paragraph('Diretora',styleAss))

    doc.build(elements)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={contexto["pessoa"].nome}_{contexto["ano"]}.pdf'
    response.write(buffer.getvalue())
    buffer.close()

    return response
   
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import cm, inch
from reportlab.lib import colors
def imprimir(request, pessoa_id, ano):
   
    buffer = io.BytesIO()

    p = canvas.Canvas(buffer,landscape(A4))
    p.setStrokeColor(colors.black)
    for m in range(1,13):
        for d in range(1,32):
            p.grid([d*cm, d*cm, d*cm],[d/2*cm, d/3*cm, d/4*cm])

    p.grid([4*cm, 6*cm, 8*cm],[2*cm, 3*cm, 4*cm])
    p.showPage()
    p.save()
    buffer.seek(0)
    
   
    return FileResponse(buffer, as_attachment=True, filename='teste.pdf')