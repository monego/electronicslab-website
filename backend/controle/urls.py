#!/usr/bin/env python3

from django.urls import path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
# router.register('pessoas', views.PessoaViewSet)
# router.register('salas', views.SalaViewSet)
router.register('registros', views.ControleAcessoViewSet, basename='controleacesso')

urlpatterns = router.urls

""" urlpatterns = [
    path('', views.index, name='index'),
    path('registros', views.registros, name='registros')
] """
