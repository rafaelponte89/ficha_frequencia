from django import forms
from .models import Pessoas, Faltas, Faltas_Pessoas
from django.forms.widgets import SelectDateWidget

class formularioPessoa(forms.ModelForm):
    nome = forms.CharField(max_length=150, required=True)

    class Meta:
        model = Pessoas
        fields = ['nome']

class formularioTF(forms.ModelForm):

    tipo = forms.CharField(max_length=3, required=True)
    descricao = forms.CharField(max_length=30, required=True)

    class Meta:
        model = Faltas
        fields = ['tipo','descricao']

class formularioLF(forms.ModelForm):

    pessoa = forms.ModelChoiceField(queryset=Pessoas.objects.all(),
                                      widget=forms.HiddenInput())
    data =  forms.DateField(
    widget=SelectDateWidget(
        
    ),
)
    # falta = forms.ModelChoiceField(queryset=Faltas.objects.all(),
    #                                   widget=forms.HiddenInput())

    class Meta:
        model = Faltas_Pessoas
        fields = ['data','falta','pessoa']