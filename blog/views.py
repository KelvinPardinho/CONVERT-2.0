from django.shortcuts import render, get_object_or_404
from .models import Post, Category

def blog_index(request):
    all_posts = Post.objects.filter(is_published=True)
    featured_post = all_posts.filter(is_featured=True).first()
    
    if featured_post:
        recent_posts = all_posts.exclude(pk=featured_post.pk)[:6]
    else:
        recent_posts = all_posts[:6]

    categories = Category.objects.all()

    context = {
        'featured_post': featured_post,
        'recent_posts': recent_posts,
        'categories': categories,
    }
    
    return render(request, 'blog/index.html', context)

def detalhe_artigo(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    context = {
        'post': post
    }
    return render(request, 'blog/detalhe_artigo.html', context)