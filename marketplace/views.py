from django.shortcuts import render, get_object_or_404
from .models import Store, Product, ProductCategory
from django.core.paginator import Paginator

def marketplace_index(request, category_slug=None, store_slug=None):
    stores = Store.objects.all()
    categories = ProductCategory.objects.all()
    
    product_list = Product.objects.filter(is_active=True).select_related('store', 'category')
    
    current_category = None
    current_store = None
    
    # Aplica filtros
    if category_slug:
        current_category = get_object_or_404(ProductCategory, slug=category_slug)
        product_list = product_list.filter(category=current_category)

    if store_slug:
        current_store = get_object_or_404(Store, slug=store_slug)
        product_list = product_list.filter(store=current_store)

    # Paginação
    paginator = Paginator(product_list.order_by('-created_at'), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'stores': stores,
        'categories': categories,
        'products': page_obj,
        'current_category': current_category,
        'current_store': current_store,
    }
    return render(request, 'marketplace/index.html', context)