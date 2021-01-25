from django.contrib import admin
from .models import user_account


@admin.register(user_account)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name','last_name','username')

