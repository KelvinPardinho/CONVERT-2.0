from django.shortcuts import render, get_object_or_404
from .models import Post, Category

def blog_index(request):
    # SUA LÓGICA ORIGINAL RESTAURADA, POIS ELA ESTAVA CORRETA
    all_posts = Post.objects.filter(is_published=True).order_by('-created_at')
    featured_post = all_posts.filter(is_featured=True).first()
    
    if featured_post:
        # Pega os 6 posts mais recentes, excluindo o que já está em destaque
        recent_posts = all_posts.exclude(pk=featured_post.pk)[:6]
    else:
        # Se não há destaque, pega os 6 mais recentes da lista completa
        recent_posts = all_posts[:6]

    categories = Category.objects.all()

    context = {
        'featured_post': featured_post,
        'recent_posts': recent_posts, # Voltamos a usar 'recent_posts'
        'categories': categories,
    }
    
    return render(request, 'blog/index.html', context)

# A view para a página de detalhes
def detalhe_artigo(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    context = {
        'post': post
    }
    return render(request, 'blog/detalhe_artigo.html', context)