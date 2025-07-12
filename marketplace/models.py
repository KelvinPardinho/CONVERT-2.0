from django.db import models
from django.utils.text import slugify

class ProductCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self): return self.name
    class Meta: verbose_name, verbose_name_plural, ordering = "Categoria de Produto", "Categorias de Produtos", ['name']

class Store(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome da Loja")
    slug = models.SlugField(max_length=100, unique=True, blank=True) # Campo slug é essencial
    logo = models.ImageField(upload_to='store_logos/', blank=True, null=True, verbose_name="Logo")
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self): return self.name
    class Meta: verbose_name, verbose_name_plural, ordering = "Loja de Afiliado", "Lojas de Afiliados", ['name']

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nome do Produto")
    description = models.TextField(blank=True, verbose_name="Descrição")
    image_url = models.URLField(max_length=500, verbose_name="URL da Imagem do Produto")
    affiliate_link = models.URLField(max_length=500, verbose_name="Link de Afiliado")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products", verbose_name="Loja")
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoria")
    is_active = models.BooleanField(default=True, verbose_name="Está Ativo?")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name
    class Meta: verbose_name, verbose_name_plural, ordering = "Produto Afiliado", "Produtos Afiliados", ['-created_at']