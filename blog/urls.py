from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('artigo/<slug:slug>/', views.detalhe_artigo, name='detalhe_artigo'),
    path('categoria/<slug:slug>/', views.category_view, name='category'),
    path('buscar/', views.search_view, name='search'),
]