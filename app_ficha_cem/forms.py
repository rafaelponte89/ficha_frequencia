from django import forms
from .models import Pessoas, Faltas, Faltas_Pessoas
from django.forms.widgets import SelectDateWidget
from django.utils.timezone import now
class formularioPessoa(forms.ModelForm):
    nome = forms.CharField(max_length=150, required=True)
    admissao =  forms.DateField(initial=now,
    widget=SelectDateWidget(months={1:'Janeiro', 
                                    2:'Fevereiro',
                                    3:'Março', 4: 'Abril', 5:'Maio', 6:'Junho', 
                                    7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro',
                                    11:'Novembro', 12:'Dezembro'}, ) 
    )
    class Meta:
        model = Pessoas
        fields = ['nome','admissao']

# formulário tipo de faltas
class formularioTF(forms.ModelForm):

    tipo = forms.CharField(max_length=3, required=True)
    descricao = forms.CharField(max_length=30, required=True)

    class Meta:
        model = Faltas
        fields = ['tipo','descricao']

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