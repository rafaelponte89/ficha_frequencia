from django import forms
from .models import Pessoas, Faltas_Pessoas, Pontuacoes, Cargos
from django.forms.widgets import SelectDateWidget, RadioSelect
from django.utils.timezone import now
from .models import Pessoas


# formulário lançamento de faltas
class formularioLF(forms.ModelForm):

    pessoa = forms.ModelChoiceField(queryset=Pessoas.objects.all(),
                                      widget=forms.HiddenInput())
    data =  forms.DateField(initial=now,
    widget=SelectDateWidget(months={1:'Janeiro', 
                                    2:'Fevereiro',
                                    3:'Março', 4: 'Abril', 5:'Maio', 6:'Junho', 
                                    7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro',
                                    11:'Novembro', 12:'Dezembro'}, ) 
                                    
                                   )
   
    qtd_dias = forms.IntegerField()

    class Meta:
        model = Faltas_Pessoas
        fields = ['data','falta','pessoa','qtd_dias']

class formularioPontuacao(forms.ModelForm):
    ano = forms.CharField(max_length=5)
    cargo = forms.CharField(max_length=5)
    funcao = forms.CharField(max_length=5)
    ue = forms.CharField(max_length=5)
    pessoa = forms.ModelChoiceField(queryset=Pessoas.objects.all(),
                                      widget=forms.HiddenInput())

    class Meta:
        model = Pontuacoes
        fields = ['ano','cargo','funcao','ue','pessoa']

class formularioAtribuicao(forms.ModelForm):
    pass