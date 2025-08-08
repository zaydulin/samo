from django.contrib import admin
from .models import *

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["user", "status", "created_timestamp"]
    list_display_links = ["user", "status", "created_timestamp"]
    save_as = True
    save_on_top = True

@admin.register(PaymentType)
class PaymentTypeAdmin(admin.ModelAdmin):
    list_display = ["shop_key", 'type']
    save_as = True
    save_on_top = True