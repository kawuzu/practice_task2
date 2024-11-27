from django.contrib import admin
from .models import Category, DesignRequest

# Register your models here.
if admin.site.is_registered(Category):
    admin.site.unregister(Category)

admin.site.register(Category)

class DesignRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'created_at')
    list_filter = ('user', 'category', 'created_at')
    search_fields = ('title', 'description')

admin.site.register(DesignRequest, DesignRequestAdmin)