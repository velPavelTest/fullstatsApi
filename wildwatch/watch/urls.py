from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'subscription', views.SubscriptionViewSet, basename='subscription')


urlpatterns = [
    path('api/alternative/', include(router.urls)),
    path('api/subscription/', views.SubscriptionsListAddViews.as_view(), name='subscriptions'),
    path('api/subscription/<int:vendor_code>/', views.SubscriptionsDellViews.as_view(), name='delete_subscription'),
    path('api/report/<int:vendor_code>/', views.ProductReport.as_view(), name='product_report'),
]
