from django.urls import path
from . import views

urlpatterns = [
    path('api/v1/user/register/', views.UserRegister.as_view(), name='user-list'),
    path('api/v1/user/login/', views.UserLogin.as_view(), name='user-login'),
    path('api/v1/check/user/', views.CheckUserExistence.as_view(), name='check-user-existence'),
]