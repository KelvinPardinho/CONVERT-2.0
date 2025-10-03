from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

class BlogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Descrição")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Categoria do Blog"
        verbose_name_plural = "Categorias do Blog"
        ordering = ['name']

class BlogPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = RichTextField(verbose_name="Conteúdo")
    excerpt = models.TextField(max_length=300, blank=True, verbose_name="Resumo")
    cover_image = models.ImageField(upload_to='blog_covers/', blank=True, null=True, verbose_name="Imagem de Capa")
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoria")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Autor")
    
    # Campos para destaque e ordenação
    is_featured = models.BooleanField(default=False, verbose_name="Artigo em Destaque")
    featured_order = models.IntegerField(default=0, verbose_name="Ordem do Destaque")
    
    # Campos de controle
    is_published = models.BooleanField(default=True, verbose_name="Publicado")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Meta Description")
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name="Meta Keywords")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Gerar excerpt automaticamente se não fornecido
        if not self.excerpt and self.content:
            # Remove tags HTML e pega os primeiros 300 caracteres
            import re
            clean_content = re.sub('<.*?>', '', self.content)
            self.excerpt = clean_content[:297] + '...' if len(clean_content) > 300 else clean_content
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:detalhe_artigo', kwargs={'slug': self.slug})
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Post do Blog"
        verbose_name_plural = "Posts do Blog"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_published', 'created_at']),
            models.Index(fields=['is_featured', 'featured_order']),
        ]

# Aliases para compatibilidade (caso alguém importe os nomes antigos)
Post = BlogPost
Category = BlogCategory