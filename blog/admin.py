from django.contrib import admin
from .models import Post, Category 

# Configuração para exibir os Posts no Admin
@admin.register(Post) # Registra o modelo 'Post'
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_published', 'created_at')
    list_filter = ('is_published', 'category', 'author')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    list_editable = ('is_published',) # Permite editar o status de publicação diretamente na lista
    
    # Melhora a exibição para o campo de autor
    raw_id_fields = ('author',)

# Configuração para exibir as Categorias no Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)} # Preenche o slug automaticamente