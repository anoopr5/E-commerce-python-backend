from django.urls import path
from . import views

urlpatterns = [
    path('api/v1/order/', views.OrderView.as_view(), name='create/update product'),

]