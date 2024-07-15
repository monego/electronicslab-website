from django.urls import path
from .views import (
    login_view, logout_view, authenticated_view, get_token_view
)

app_name = 'authentication'

urlpatterns = [
    path('csrf/', get_token_view, name='get_csrf_token'),
    path('login/', login_view, name='api-login'),
    path('logout/', logout_view, name='api-logout'),
    path('authenticate/', authenticated_view, name='api-authenticated'),
]
