from rest_framework import serializers
from .models import Subscription


class SubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'vendor_code']
