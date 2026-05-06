"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.http import HttpResponse
from myproject.health import health_check, ready_check, api_root

urlpatterns = [
    path("", api_root, name='api-root'),
    path('health/', health_check, name='health'),
    path('ready/', ready_check, name='ready'),
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # JWT Token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
  
    # Accounts API (User Profile, Auth, Documents)
    path("api/", include("accounts.urls")),
    path("api/user/", include("accounts.urls")),
    
    # Module APIs
    path("api/doccheck/", include("modules.doccheck.urls")),
    path("api/documents/", include("modules.documents.urls")),
    path("api/orders/", include("modules.docready.urls")),
    path("api/cma/", include("modules.smartcma.urls")),
    path("api/payments/", include("modules.payments.urls")),
    path("api/operator/", include("modules.operator.urls")),
]

