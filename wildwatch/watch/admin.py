from django.contrib import admin
from .models import Subscription, ProductParseEntry


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'vendor_code')


class ProductParseEntryAdmin(admin.ModelAdmin):
    list_display = ('vendor_code', 'name', 'price_wo_discount', 'parse_time', 'seller')


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(ProductParseEntry, ProductParseEntryAdmin)
