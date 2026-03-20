from rest_framework import filters, serializers
from rest_framework.serializers import ModelSerializer
from root.models import Pessoa, Sala


class PessoaSerializer(ModelSerializer):
    queryset = Pessoa.objects.all()
    serializer_class = Pessoa
    filter_backends = [filters.SearchFilter]
    search_fields = ['matricula']
    last_access = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Pessoa
        fields = ['id', 'nome', 'email', 'telefone', 'matricula', 'tipo', 'last_access']

class SalaSerializer(ModelSerializer):
    queryset = Sala.objects.all()
    serializer_class = Sala
    filter_backends = [filters.SearchFilter]
    search_fields =  ['numero']
    e_informatica = serializers.SerializerMethodField()

    class Meta:
        model = Sala
        fields = ['id', 'predio', 'nome', 'numero', 'andar', 'codigo', 'e_informatica']

    def get_e_informatica(self, obj):
        return getattr(obj, 'e_informatica', False)
