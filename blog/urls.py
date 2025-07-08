# blog/urls.py (VERSÃO CORRIGIDA)

from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_index, name='blog_index'),
    path('<slug:slug>/', views.detalhe_artigo, name='detalhe_artigo'),
]