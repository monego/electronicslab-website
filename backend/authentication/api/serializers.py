from django.contrib.auth.models import User
from rest_framework import filters, serializers


class UserSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    serializer_class = User
    filter_backends = [filters.SearchFilter]
    search_fields =  ['id']
    class Meta:
        model = User
        fields = ['id', 'username']
