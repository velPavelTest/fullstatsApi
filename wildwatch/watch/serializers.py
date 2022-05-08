from rest_framework import serializers
from .models import Subscription, ProductParseEntry


class SubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'vendor_code']


class ProductParseEntrySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProductParseEntry
        fields = ['vendor_code', 'parse_time', 'name', 'price_wo_discount', 'price_with_discount', 'brand', 'seller']
