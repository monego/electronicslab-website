from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('atividades', views.AtividadesViewSet, basename='atividades')
router.register('ausencia', views.AusenciaViewSet, basename='ausencia')
router.register('registros', views.ControleAcessoViewSet, basename='registros')
router.register('emprestimos', views.EmprestimoViewSet, basename='emprestimos')
router.register('equipamento', views.EquipamentoViewSet, basename='equipamentos')
router.register('horarios', views.HorarioTrabalhoViewSet, basename='horario_trabalho')
router.register('manutencao', views.ManutencaoViewSet, basename='manutencao')

app_name = 'controle'

urlpatterns = [
    path('', include(router.urls))
]

router = routers.DefaultRouter()
