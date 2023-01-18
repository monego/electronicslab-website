#!/usr/bin/env python3
from django.forms import ModelForm
from .models import Pessoa

class PessoaForm(ModelForm):
    class Meta:
        model = Pessoa
        fields = '__all__'
