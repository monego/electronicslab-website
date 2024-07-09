from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def login_view(request):

    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'username': username})
        else:
            return JsonResponse({'success': False, 'error': 'Credenciais inválidas'})
    else:
        return JsonResponse({'authenticated': False})

@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({'authenticated': False})
