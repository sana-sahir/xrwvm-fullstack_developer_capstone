from django.contrib import admin
from .models import CarMake, CarModel

class CarModelInline(admin.TabularInline):
    model = CarModel
    extra = 1  # Number of empty forms to show by default

class CarMakeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'updated_at']
    search_fields = ['name']
    list_filter = ['created_at']
    inlines = [CarModelInline]  # Allow editing car models directly within CarMake

class CarModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'car_make', 'type', 'year', 'created_at', 'updated_at']
    search_fields = ['name', 'car_make__name']  # Search by both car model and car make
    list_filter = ['type', 'year', 'car_make__name']
    ordering = ['car_make__name', 'name']  # Sort by make and then by model name

# Register the models

# Register models here
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)