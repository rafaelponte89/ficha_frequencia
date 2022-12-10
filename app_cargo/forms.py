from django import forms
from .models import Cargos

class formularioCargo(forms.ModelForm):
    cargo = forms.CharField(max_length=50, required=True)

    class Meta:
        model = Cargos
        fields=['cargo']