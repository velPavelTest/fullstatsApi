from rest_framework import viewsets
from rest_framework import generics
from .models import Subscription, ProductParseEntry
from .serializers import SubscriptionSerializer, ProductParseEntrySerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.utils import timezone


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    API endpoint управления своими подписками на артикулы Wild
    """
    # @task предложить альтернативный API. Без update и по кодам артикулов.
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    def get_queryset(self):
        user = self.request.user
        return Subscription.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]


class ProductReport(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductParseEntrySerializer

    def get_queryset(self):
        """
        Return a list of all users.
        """
        vendor_code = self.kwargs['vendor_code']
        start = self.request.query_params.get('start', timezone.localtime().date())
        end = self.request.query_params.get('end', timezone.localtime().date())
        period = int(self.request.query_params.get('period', 1))
        how_much_hours = int(24/period)
        hours = (i*period for i in range(how_much_hours))
        f = ProductParseEntry.objects.filter(vendor_code=vendor_code).filter(parse_time__date__range=(start, end))\
            .filter(parse_time__hour__in=hours)
        # Следующая строка работает ТОЛЬКО на PostgreSQL. При смене БД по другому очищайте от дубликатов в рамках часа
        f = f.order_by('vendor_code', 'parse_time__date', 'parse_time__hour', 'parse_time')\
            .distinct('vendor_code', 'parse_time__date', 'parse_time__hour')
        return f
