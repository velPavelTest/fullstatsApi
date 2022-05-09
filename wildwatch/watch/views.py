from rest_framework import viewsets
from rest_framework import generics
from .models import Subscription, ProductParseEntry
from .serializers import SubscriptionSerializer, ProductParseEntrySerializer, SubscriptionWoIdSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from dateutil.parser import parse
from django.shortcuts import get_object_or_404


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    АЛЬТЕРНАТИВНЫЙ API endpoint управления своими подписками на артикулы Wild. С использованием ID
    """
    # @task удалить после согласования один из API ----- предложить альтернативный API. Без update и по кодам артикулов.
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    def get_queryset(self):
        user = self.request.user
        return Subscription.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]


class SubscriptionsListAddViews(generics.ListCreateAPIView):
    """API endpoint просмотра и создания подписок на артикулы Wild. Без ID. Всё управление через артикулы.
    """
    serializer_class = SubscriptionWoIdSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Subscription.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SubscriptionsDellViews(generics.DestroyAPIView):
    """API endpoint удаления подписок Wild. Принимает артикул.
    """
    serializer_class = SubscriptionWoIdSerializer
    permission_classes = [IsAuthenticated]
    lookup_fields = ['vendor_code']

    def get_queryset(self):
        user = self.request.user
        return Subscription.objects.filter(user=user)

    def get_object(self):
        queryset = self.get_queryset()
        filter = {}
        for field in self.lookup_fields:
            filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)
        return obj


class ProductReport(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductParseEntrySerializer

    def get_queryset(self):
        """
        Возвращает отчёт по продукту в выбранном интервале дат, с выбранном периодом.
        Params:
            - start - start date 2022-12-20
            - end - end date 2022-12-20
            - period:int - period (hours)
        """
        vendor_code = self.kwargs['vendor_code']
        try:
            start = self.request.query_params.get('start', timezone.localtime().date())
            if type(start) == str:
                start = parse(start).date()
            end = self.request.query_params.get('end', timezone.localtime().date())
            if type(end) == str:
                end = parse(end).date()
        except BaseException:
            raise ValidationError(dict(message='Start и End даты должны быть формате YYYY-MM-DD Например, 2022-12-20'))
        try:
            period = int(self.request.query_params.get('period', 1))
        except BaseException:
            raise ValidationError(dict(message='Введите период один из 1, 2, 3, 4, 6, 8, 12, 24'))
        if 24 % period != 0:
            raise ValidationError(dict(message='Введите период один из 1, 2, 3, 4, 6, 8, 12, 24'))

        how_much_hours = int(24/period)
        hours = (i*period for i in range(how_much_hours))
        f = ProductParseEntry.objects.filter(vendor_code=vendor_code).filter(parse_time__date__range=(start, end))\
            .filter(parse_time__hour__in=hours)
        # Следующая строка работает ТОЛЬКО на PostgreSQL.
        # При смене БД по другому очищайте от возможных дубликатов в рамках часа
        f = f.order_by('vendor_code', 'parse_time__date', 'parse_time__hour', 'parse_time')\
            .distinct('vendor_code', 'parse_time__date', 'parse_time__hour')
        return f
