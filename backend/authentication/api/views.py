from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
import json


def get_token_view(request):
    token = get_token(request)
    return JsonResponse({'csrftoken': token})

def login_view(request):

    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            first_name = request.user.first_name
            last_initial = request.user.last_name[0] if request.user.last_name else ""
            return JsonResponse(
                {'success': True,
                'username': username,
                'short_name': f'{first_name} {last_initial}.',
                'is_staff': user.is_staff,
            })
        else:
            return JsonResponse({'success': False, 'error': 'Credenciais inválidas'})
    else:
        return JsonResponse({'authenticated': False})

def logout_view(request):
    logout(request)
    return JsonResponse({'authenticated': False})
