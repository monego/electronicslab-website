#!/usr/bin/env python3

from django.urls import path, include
from . import views
from rest_framework import routers


router = routers.DefaultRouter()
router.register('equipamento', views.EquipamentoViewSet, basename='equipamentos')


urlpatterns = [
    path('', include(router.urls)),
]

# urlpatterns += router.urls
