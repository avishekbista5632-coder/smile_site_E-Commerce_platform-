from django.contrib import admin
from .models import Product, ProductImage, Order, OrderItem
from django.utils.html import format_html

# Inline for gallery images
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ('thumbnail',)

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="object-fit:cover;"/>', obj.image.url)
        return "-"
    thumbnail.short_description = "Thumbnail"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "description")
    search_fields = ("name",)
    inlines = [ProductImageInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ("product", "quantity", "price_at_purchase")
    extra = 0
# Main Product admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "user", "email", "contact", "total_amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email", "contact", "user__username")
    inlines = [OrderItemInline]
    readonly_fields = ("total_amount", "created_at")  # prevent accidental changes

# Register the other models
admin.site.register(ProductImage)

