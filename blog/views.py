from django.shortcuts import render
from .models import Post, Category



def blog_index(request):
    # Busca todos os posts que estão marcados como "publicados"
    all_posts = Post.objects.filter(is_published=True)
    
    # Busca o post em destaque (o mais recente marcado como destaque)
    featured_post = all_posts.filter(is_featured=True).first()
    
    # Exclui o post em destaque da lista de posts recentes para não repetir
    if featured_post:
        recent_posts = all_posts.exclude(pk=featured_post.pk)[:6] # Pega os 6 mais recentes
    else:
        recent_posts = all_posts[:6]

    # Busca todas as categorias
    categories = Category.objects.all()

    context = {
        'featured_post': featured_post,
        'recent_posts': recent_posts,
        'categories': categories,
    }
    
    return render(request, 'blog/index.html', context) # Assumindo que seu template se chama index.html dentro de blog/templates/blog/