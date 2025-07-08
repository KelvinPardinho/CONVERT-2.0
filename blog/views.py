from django.shortcuts import render, get_object_or_404
from .models import Post, Category

def blog_index(request):
    # Busca todos os posts publicados, ordenados do mais recente para o mais antigo
    all_posts = Post.objects.filter(is_published=True).order_by('-created_at')
    
    # Tenta encontrar um post em destaque
    featured_post = all_posts.filter(is_featured=True).first()
    
    # Busca todas as categorias
    categories = Category.objects.all()

    context = {
        'featured_post': featured_post,
        # CORREÇÃO: Passa a lista COMPLETA de todos os posts para o template.
        # O template decidirá se mostra o título "Outros Artigos" ou "Todos os Artigos".
        'all_posts': all_posts, 
        'categories': categories,
    }
    
    return render(request, 'blog/index.html', context)

def detalhe_artigo(request, slug):
    # Esta view já está correta, mas a incluímos para garantir
    post = get_object_or_404(Post, slug=slug, is_published=True)
    context = {
        'post': post
    }
    return render(request, 'blog/detalhe_artigo.html', context)