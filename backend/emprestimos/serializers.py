from rest_framework.serializers import ModelSerializer

from .models import Equipamento

class EquipamentoSerializer(ModelSerializer):

    class Meta:
        model = Equipamento
        fields = '__all__'