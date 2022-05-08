from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'subscription', views.SubscriptionViewSet, basename='subscription')


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/report/<int:vendor_code>/', views.ProductReport.as_view(), name='product_report')
]
