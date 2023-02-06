from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from root.models import Pessoa, Sala
from .models import ControleAcesso
from .serializers import PessoaSerializer, SalaSerializer, ControleAcessoSerializer
from rest_framework.viewsets import ModelViewSet


class PessoaViewSet(ModelViewSet):
    queryset = Pessoa.objects.all()
    serializer_class = PessoaSerializer


class SalaViewSet(ModelViewSet):
    queryset = Sala.objects.all()
    serializer_class = SalaSerializer


class ControleAcessoViewSet(ModelViewSet):
    queryset = ControleAcesso.objects.all()
    serializer_class = ControleAcessoSerializer


""" def index(request):

    pessoas = [] """

"""     i = 0

    for pessoa in Pessoa.objects.all():
        pessoas.append({
            'nome': pessoa.nome,
            'tipo': pessoa.tipo
        }) """
