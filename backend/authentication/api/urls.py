from django.urls import path
from .views import LoginView, UserView

app_name = 'authentication'

urlpatterns = [
    path('login/', LoginView.as_view(), name='api-login'),
    path('user/', UserView.as_view(), name='api-user'),
]
