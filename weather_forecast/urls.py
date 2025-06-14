from django.urls import path
from .views import *

urlpatterns = [
    # Class-based view for listing forecasts
    path('forecasts/list/', ForecastListView.as_view(), name='forecast_list'),
    # Function-based views for various forecast operations
    path('forecasts/', get_all_forecasts, name='get_all_forecasts'),
    path('forecasts/create/', create_forecast, name='create_forecast'),
    path('forecasts/delete/<int:forecast_id>/', delete_forecast, name='delete_forecast'),
    path('forecasts/toggle-alert/<int:forecast_id>/', toggle_weather_alert, name='toggle_weather_alert'),
]
