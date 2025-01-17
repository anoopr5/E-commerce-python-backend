from django.urls import path
from . import views

urlpatterns = [
    path('api/v1/product/', views.ProductView.as_view(), name='create/update product'),
    path('api/v1/check/product/', views.CheckProductAvailability.as_view(), name='check-product-availability'),

]