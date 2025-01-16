from django.urls import path
from . import views

urlpatterns = [
    path('api/v1/product/', views.ProductView.as_view(), name='create/update product'),

]