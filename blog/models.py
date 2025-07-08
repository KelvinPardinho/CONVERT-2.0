from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Category(models.Model):
    # ... (seu modelo Category está perfeito, não mude nada) ...
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    # ================== CAMPO ADICIONADO ==================
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="Slug (URL)")
    # ======================================================
    content = models.TextField(verbose_name="Conteúdo")
    cover_image = models.ImageField(upload_to='blog_covers/', blank=True, null=True, verbose_name="Imagem de Capa")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Autor")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoria")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    is_published = models.BooleanField(default=False, verbose_name="Publicado?")
    is_featured = models.BooleanField(default=False, verbose_name="É Destaque?")

    # Sobrescreve o método save para gerar o slug automaticamente
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ['-created_at']