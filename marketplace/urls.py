from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.marketplace_index, name='marketplace_index'),
    path('categoria/<slug:category_slug>/', views.marketplace_index, name='products_by_category'),
    path('loja/<slug:store_slug>/', views.marketplace_index, name='products_by_store'),
]