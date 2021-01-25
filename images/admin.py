from django.contrib import admin
from .models import Links, Images
# Register your models here.
@admin.register(Links)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user','link')

@admin.register(Images)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user','image','thumb')