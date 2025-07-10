# blog/views.py (VERSÃO FINAL E UNIFICADA)

from django.shortcuts import render, get_object_or_404
from .models import Post, Category

def blog_index(request):
    # 1. Busca todos os posts publicados, do mais recente para o mais antigo.
    all_posts = Post.objects.filter(is_published=True).order_by('-created_at')
    
    # 2. Encontra o post em destaque, se houver.
    featured_post = all_posts.filter(is_featured=True).first()
    
    # 3. Busca todas as categorias para o filtro.
    categories = Category.objects.all()

    context = {
        'featured_post': featured_post,
        # 4. Passa a lista COMPLETA de posts para o template.
        #    Isso garante que o destaque também apareça na lista principal se o usuário quiser ver tudo.
        'all_posts': all_posts,
        'categories': categories,
    }
    
    return render(request, 'blog/index.html', context)

def detalhe_artigo(request, slug):
    # Busca o post atual que o usuário está lendo
    post = get_object_or_404(Post.objects.select_related('author', 'category'), slug=slug, is_published=True)
    
    # Busca os 5 posts mais recentes para a barra lateral, excluindo o post atual
    recent_posts = Post.objects.filter(is_published=True).exclude(pk=post.pk).order_by('-created_at')[:5]
    
    context = {
        'post': post,
        'recent_posts': recent_posts,
    }
    return render(request, 'blog/detalhe_artigo.html', context)