from rest_framework import viewsets
from .models import Subscription
from .serializers import SubscriptionSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers


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
