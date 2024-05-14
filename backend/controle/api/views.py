from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from root.models import Pessoa, Sala
from controle.models import ControleAcesso
from .serializers import PessoaSerializer, SalaSerializer, ControleAcessoSerializer
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import generics


class PessoaViewSet(ModelViewSet):
    serializer_class = PessoaSerializer

    def get_queryset(self):
        queryset = Pessoa.objects.all()
        matricula = self.request.query_params.get('matricula')
        if matricula is not None:
            queryset = queryset.filter(matricula=matricula)
        return queryset


class SalaViewSet(ModelViewSet):
    serializer_class = SalaSerializer
    queryset = Sala.objects.all()
    def get_queryset(self):
        queryset = Sala.objects.all()
        numero = self.request.query_params.get('numero')
        if numero is not None:
            queryset = queryset.filter(numero=numero)
        return queryset


class ControleAcessoViewSet(ModelViewSet):
    serializer_class = ControleAcessoSerializer
    queryset = ControleAcesso.objects.all()
    def hora_saida_is_null(self):
        queryset = ControleAcesso.objects.filter(hora_saida_isnull=True)
        print(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
