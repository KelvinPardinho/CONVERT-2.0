# blog/views.py (VERSÃO FINAL E SEGURA)

from django.shortcuts import render, get_object_or_404
from .models import Post, Category

def blog_index(request):
    # Começa com todos os posts publicados, ordenados do mais recente para o mais antigo
    all_posts = Post.objects.filter(is_published=True).order_by('-created_at')
    
    # Tenta encontrar um post em destaque
    featured_post = all_posts.filter(is_featured=True).first()
    
    # Lista para os outros posts (não em destaque)
    other_posts = all_posts

    # --- LÓGICA CORRIGIDA E SEGURA ---
    # Se um post em destaque FOI encontrado, nós o removemos da lista de 'outros posts'
    if featured_post:
        other_posts = all_posts.exclude(pk=featured_post.pk)

    categories = Category.objects.all()

    context = {
        'featured_post': featured_post,
        # Passa a lista de 'outros_posts' para o template
        'other_posts': other_posts,
        'categories': categories,
    }
    
    return render(request, 'blog/index.html', context)

def detalhe_artigo(request, slug):
    # Esta view já estava correta, mas a incluímos para garantir
    post = get_object_or_404(Post, slug=slug, is_published=True)
    context = {
        'post': post
    }
    return render(request, 'blog/detalhe_artigo.html', context)