#!/usr/bin/env python3
from django.forms import ModelForm
from .models import Disciplina

class DisciplinaForm(ModelForm):
    class Meta:
        model = Disciplina
        fields = '__all__'
