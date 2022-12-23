from django import forms
from django.forms.widgets import SelectDateWidget
from app_cargo.models import Cargos
from .models import Pessoas
from django.utils.timezone import now
from datetime import date
from bootstrap_datepicker_plus.widgets import DatePickerInput

class formularioPessoa(forms.ModelForm):
    cargos = Cargos.objects.all()



    id = forms.CharField(max_length=6, required=True)
    nome = forms.CharField(max_length=150, required=True)

        
    dt_nasc =  forms.DateField(widget=DatePickerInput(), label="Data de Nascimento")

    cpf = forms.CharField(max_length=11, required=True, label='CPF')
    efetivo = forms.ChoiceField(choices=Pessoas.EFETIVO,widget= forms.RadioSelect)
    cargo = forms.ModelChoiceField(queryset=cargos)
   
    admissao =  forms.DateField(widget=DatePickerInput(), label="Data de Admissão")

    saida = forms.DateField(widget=DatePickerInput(), label="Data de Saída", required=False)

    class Meta:
        model = Pessoas
        fields = ['id','nome','dt_nasc','cpf','admissao','saida','efetivo','cargo']
        widget = {
            "dt_nasc": DatePickerInput(),
            "admissao": DatePickerInput(),
            "saida": DatePickerInput()
           
        }
