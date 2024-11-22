from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('aulas', views.AulasViewSet, basename='aulas')

app_name = 'aulas_api'

urlpatterns = [
    path('', include(router.urls))
]

router = routers.DefaultRouter()
