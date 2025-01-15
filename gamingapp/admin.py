from django.contrib import admin
from .models import Store, Review

# Register your models here.

class StoreAdmin(admin.ModelAdmin):
    list_display = ['title']

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['comment']

admin.site.register(Store, StoreAdmin)
admin.site.register(Review, ReviewAdmin)