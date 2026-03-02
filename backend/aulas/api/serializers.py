from aulas.models import Aula
from rest_framework import filters
from rest_framework.serializers import ModelSerializer
import rest_framework.serializers as serializers


class AulaSerializer(ModelSerializer):
    queryset = Aula.objects.all()
    serializer_class = Aula
    sala_andar = serializers.SerializerMethodField()
    sala_codigo = serializers.SerializerMethodField()
    sala_numero = serializers.SerializerMethodField()
    sala_nome = serializers.SerializerMethodField()
    sala_e_informatica = serializers.SerializerMethodField()
    filter_backends = [filters.SearchFilter]
    search_fields = ['disciplina', 'professor']

    class Meta:
        model = Aula
        fields = [
            "professor",
            "disciplina",
            "inicio",
            "fim",
            "sala",
            "sala_codigo",
            "sala_nome",
            "sala_numero",
            "sala_andar",
            "sala_e_informatica",
        ]

    def get_sala_e_informatica(self, obj):
        return getattr(obj.sala, 'e_informatica', False) if obj.sala else False

    def get_sala_andar(self, obj):
        return obj.sala.andar if obj.sala else None

    def get_sala_codigo(self, obj):
        return obj.sala.codigo if obj.sala else None

    def get_sala_nome(self, obj):
        return obj.sala.nome if obj.sala else None

    def get_sala_numero(self, obj):
        return obj.sala.numero if obj.sala else None
