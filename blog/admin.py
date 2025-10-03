from django.contrib import admin
from .models import BlogPost, BlogCategory

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'is_featured', 'is_published', 'created_at']
    list_filter = ['category', 'is_published', 'is_featured', 'created_at', 'author']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Conteúdo', {
            'fields': ('title', 'slug', 'content', 'excerpt', 'cover_image')
        }),
        ('Classificação', {
            'fields': ('category', 'author')
        }),
        ('Destaque', {
            'fields': ('is_featured', 'featured_order'),
            'description': 'Marque como destaque e defina a ordem para aparecer no topo da página'
        }),
        ('Publicação', {
            'fields': ('is_published',)
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo post
            obj.author = request.user
        super().save_model(request, obj, form, change)