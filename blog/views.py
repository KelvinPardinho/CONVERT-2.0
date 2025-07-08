# blog/views.py (VERSÃO FINAL COM CAMINHOS DE TEMPLATE CORRIGIDOS)

from django.shortcuts import render, get_object_or_404
from .models import Post, Category

def blog_index(request):
    all_posts = Post.objects.filter(is_published=True)
    featured_post = all_posts.filter(is_featured=True).first()
    
    if featured_post:
        other_posts = all_posts.exclude(pk=featured_post.pk)
    else:
        other_posts = all_posts

    categories = Category.objects.all()

    context = {
        'featured_post': featured_post,
        'other_posts': other_posts,
        'categories': categories,
    }
    
    # CORREÇÃO: Removido o caminho redundante do template.
    return render(request, 'blog/index.html', context)

def detalhe_artigo(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    context = {
        'post': post
    }
    # CORREÇÃO: Removido o caminho redundante do template.
    return render(request, 'blog/detalhe_artigo.html', context)