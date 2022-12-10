from django import forms
from django.forms.widgets import SelectDateWidget
from app_cargo.models import Cargos
from .models import Pessoas
from django.utils.timezone import now

class formularioPessoa(forms.ModelForm):
    cargos = Cargos.objects.all()
    id = forms.CharField(max_length=6, required=True)
    nome = forms.CharField(max_length=150, required=True)
    dt_nasc =  forms.DateField(initial=now,
    widget=SelectDateWidget(months={1:'Janeiro', 
                                    2:'Fevereiro',
                                    3:'Março', 4: 'Abril', 5:'Maio', 6:'Junho', 
                                    7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro',
                                    11:'Novembro', 12:'Dezembro'}, ), label='Data de Nascimento: '
    )
    cpf = forms.CharField(max_length=11, required=True, label='CPF')
    efetivo = forms.ChoiceField(choices=Pessoas.EFETIVO,widget= forms.RadioSelect)
    cargo = forms.ModelChoiceField(queryset=cargos)

    admissao =  forms.DateField(initial=now,
    widget=SelectDateWidget(months={1:'Janeiro', 
                                    2:'Fevereiro',
                                    3:'Março', 4: 'Abril', 5:'Maio', 6:'Junho', 
                                    7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro',
                                    11:'Novembro', 12:'Dezembro'}, ), label='Data de Admissão'
    )
    class Meta:
        model = Pessoas
        fields = ['id','nome','dt_nasc','cpf','admissao','efetivo','cargo']
