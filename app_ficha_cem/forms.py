from django import forms
from .models import Pessoas, Faltas_Pessoas, Pontuacoes, Cargos
from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.utils.timezone import now
from .models import Pessoas


# formulário lançamento de faltas
class formularioLF(forms.ModelForm):
  
    pessoa = forms.ModelChoiceField(queryset=Pessoas.objects.all(),
                                      widget=forms.HiddenInput())
    data =  forms.DateField(initial=now,
    widget= DatePickerInput()
                                   )
    
    qtd_dias = forms.IntegerField()


    class Meta:
        model = Faltas_Pessoas
        fields = ['data','falta','pessoa','qtd_dias']
        widgets = {
            'data': DatePickerInput()
        }

class formularioPontuacao(forms.ModelForm):
    ano = forms.IntegerField(min_value=0)
    funcao = forms.IntegerField(min_value=0)
    cargo = forms.IntegerField(min_value=0)
    
    ue = forms.IntegerField(min_value=0)

   
    pessoa = forms.ModelChoiceField(queryset=Pessoas.objects.all(),
                                      widget=forms.HiddenInput())

    class Meta:
        model = Pontuacoes
        # fields = ['ano','cargo','funcao','ue','pessoa',]
        fields = ['ano','funcao','cargo','ue','pessoa']
