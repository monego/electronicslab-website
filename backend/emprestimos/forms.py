#!/usr/bin/env python3
#!/usr/bin/env python3
from django.forms import ModelForm
from .models import Emprestimo

class EmprestimoForm(ModelForm):
    class Meta:
        model = Emprestimo
        fields = '__all__'
