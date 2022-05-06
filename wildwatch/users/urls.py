from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from . import views

app_name = "users"

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("register/", views.register_request, name="register"),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/testaccess/', views.TestAcces.as_view(), name='test_access'),
]
