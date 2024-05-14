from django.contrib.auth import authenticate
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token


class LoginView(APIView):
    permission_classes = []
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = []
    
    def post(self, request):
        # Delete the token associated with the current user
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_200_OK)
