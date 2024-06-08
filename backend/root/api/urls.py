#!/usr/bin/env python3

from django.urls import path, include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register('pessoas', views.PessoaViewSet, basename='pessoas')
router.register('salas', views.SalaViewSet, basename='salas')

app_name = 'root'

urlpatterns = [
    path('', include(router.urls))
]
