from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('ausencia', views.AusenciaViewSet, basename='ausencia')
router.register('compras', views.ComprasViewSet, basename='compras')
router.register('registros', views.ControleAcessoViewSet, basename='registros')
router.register('emprestimos', views.EmprestimoViewSet, basename='emprestimos')
router.register('items', views.ItemViewSet, basename='items')
router.register('equipamento', views.EquipamentoViewSet, basename='equipamentos')
router.register('materiais', views.EquipamentoPublicoViewSet, basename='materiais')
router.register('horarios', views.HorarioTrabalhoViewSet, basename='horario_trabalho')
router.register('manutencao', views.ManutencaoViewSet, basename='manutencao')
router.register('orcamento', views.OrcamentoViewSet, basename='orcamento')
router.register('users', views.UserViewSet)

app_name = 'controle'

urlpatterns = [
    path('', include(router.urls))
]

router = routers.DefaultRouter()
