from .models import Product

def products_context(request):
    return {
        "products": Product.objects.prefetch_related("gallery").all()
    }
