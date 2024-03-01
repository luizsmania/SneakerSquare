from django.contrib import admin
from .models import Product, Category, Comment

class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'name',
        'get_categories',
        'price',
        'rating',
        'image',
    )

    ordering = ('sku',)

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.category.all()])

    get_categories.short_description = 'Categories'

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )

class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'product',
        'text',
        'created_at',
    )

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
