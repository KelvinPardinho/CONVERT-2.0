# blog/views.py (VERSÃO CORRIGIDA)

from django.shortcuts import render, get_object_or_404
from .models import Post, Category

def blog_index(request):
    all_posts = Post.objects.filter(is_published=True)
    featured_post = all_posts.filter(is_featured=True).first()
    
    if featured_post:
        # PONTO 2 CORRIGIDO: Agora mostramos todos os outros posts
        other_posts = all_posts.exclude(pk=featured_post.pk)
    else:
        # Se não há destaque, mostramos todos os posts
        other_posts = all_posts

    categories = Category.objects.all()

    context = {
        'featured_post': featured_post,
        'other_posts': other_posts, # Mudamos o nome da variável para maior clareza
        'categories': categories,
    }
    
    return render(request, 'blog/index.html', context)

# NOVA VIEW: Para exibir um único artigo
def detalhe_artigo(request, slug):
    # Busca o post pelo slug ou retorna um erro 404 se não encontrar
    post = get_object_or_404(Post, slug=slug, is_published=True)
    context = {
        'post': post
    }
    return render(request, 'templates/blog/detalhe_artigo.html', context)