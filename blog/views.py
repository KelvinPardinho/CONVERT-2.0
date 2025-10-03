# blog/views.py (VERSÃO FINAL E UNIFICADA)

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import BlogPost, BlogCategory

def index(request):
    """
    View principal do blog com artigo em destaque e paginação
    """
    # Buscar artigo em destaque (o mais recente marcado como featured)
    featured_post = BlogPost.objects.filter(
        is_published=True, 
        is_featured=True
    ).order_by('featured_order', '-created_at').first()
    
    # Buscar todos os posts publicados, excluindo o em destaque
    posts_queryset = BlogPost.objects.filter(is_published=True)
    if featured_post:
        posts_queryset = posts_queryset.exclude(id=featured_post.id)
    
    posts_queryset = posts_queryset.order_by('-created_at')
    
    # Configurar paginação (26 posts por página)
    paginator = Paginator(posts_queryset, 26)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)
    
    # Buscar categorias para o menu
    categories = BlogCategory.objects.all()
    
    context = {
        'featured_post': featured_post,
        'posts': posts,
        'categories': categories,
        'total_posts': posts_queryset.count(),
    }
    
    return render(request, 'blog/index.html', context)

def detalhe_artigo(request, slug):
    """
    View para mostrar um artigo específico
    """
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Posts relacionados (mesma categoria, excluindo o atual)
    related_posts = BlogPost.objects.filter(
        category=post.category,
        is_published=True
    ).exclude(id=post.id).order_by('-created_at')[:4]
    
    # Posts recentes para sidebar
    recent_posts = BlogPost.objects.filter(
        is_published=True
    ).exclude(id=post.id).order_by('-created_at')[:5]
    
    context = {
        'post': post,
        'related_posts': related_posts,
        'recent_posts': recent_posts,
    }
    
    return render(request, 'blog/detalhe_artigo.html', context)

def category_view(request, slug):
    """
    View para mostrar posts de uma categoria específica
    """
    category = get_object_or_404(BlogCategory, slug=slug)
    
    posts_queryset = BlogPost.objects.filter(
        category=category,
        is_published=True
    ).order_by('-created_at')
    
    # Paginação
    paginator = Paginator(posts_queryset, 26)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'posts': posts,
        'total_posts': posts_queryset.count(),
    }
    
    return render(request, 'blog/category.html', context)

def search_view(request):
    """
    View para busca de posts
    """
    query = request.GET.get('q', '')
    posts_queryset = BlogPost.objects.filter(is_published=True)
    
    if query:
        posts_queryset = posts_queryset.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query)
        ).distinct()
    
    # Paginação
    paginator = Paginator(posts_queryset, 26)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)
    
    context = {
        'posts': posts,
        'query': query,
        'total_posts': posts_queryset.count(),
    }
    
    return render(request, 'blog/search.html', context)