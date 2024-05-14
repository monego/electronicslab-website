from django.urls import path
from .views import LoginView, LogoutView

app_name = 'authentication'

urlpatterns = [
    path('login/', LoginView.as_view(), name='api-login'),
    path('logout/', LogoutView.as_view(), name='api-logout'),
]
