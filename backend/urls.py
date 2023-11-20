from django.contrib import admin
from django.urls import path, include

from rest_framework import routers
from ikemenstore import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView
)
from ikemenstore.api import viewsets as ikemenstoreviewsets
from ikemenstore.views import EmailConfirmationView

route = routers.DefaultRouter()

route.register(r'users', ikemenstoreviewsets.UserClientViewSet, basename="Usuários")
route.register(r'register', ikemenstoreviewsets.UserRegistrationViewSet, basename="Cadastro")
route.register(r'characters', ikemenstoreviewsets.CharactersViewSet, basename="Personagens")
route.register(r'images', ikemenstoreviewsets.ImageViewSet, basename="Imagens")
route.register(r'sales', ikemenstoreviewsets.SaleViewSet, basename="Vendas")

from django.conf import settings
from django.conf.urls.static import static

# Lista de Url disponível nessa desgraça
urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('', include(route.urls)),
    path('session-user/', views.SessionUserView.as_view()),
    path('account-confirm/<str:token>/', EmailConfirmationView.as_view(), name='email-confirmation'),

    # JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)