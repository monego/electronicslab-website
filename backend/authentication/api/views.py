from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from authentication.api.serializers import UserSerializer


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Login ou senha inválido"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class UserView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                'id': request.user.id,
                'username': request.user.username,
            })
        else:
            return Response({'error': 'Usuário não autenticado'}, status=401)
