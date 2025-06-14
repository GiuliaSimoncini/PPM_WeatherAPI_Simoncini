"""
URL configuration for weather_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/weather_forecast/', include('weather_forecast.urls')),
    
    # Template views
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),
    path('forecasts/', TemplateView.as_view(template_name='forecasts.html'), name='forecasts'),
    path('profile/', TemplateView.as_view(template_name='profile.html'), name='profile'),
    path('query-history/', TemplateView.as_view(template_name='query_history.html'), name='query_history'),
]
