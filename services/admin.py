from django.contrib import admin
from .models import Category, Service, Review

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    
admin.site.register(Category, CategoryAdmin)

class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'description', 'category', 'job_limit',
    'available', 'created', 'updated']
    list_editable = ['price', 'category', 'job_limit', 'available']
    list_per_page = 20

admin.site.register(Service, ServiceAdmin)
admin.site.register(Review)
