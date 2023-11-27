#!/usr/bin/env python3

from django.urls import path
from . import views
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'equipamento', views.EquipamentoViewSet, basename='equipamentos')


urlpatterns = [

]

urlpatterns += router.urls
