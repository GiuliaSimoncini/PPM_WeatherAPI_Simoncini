from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework import generics, filters
from functools import wraps
from datetime import date
from .models import Forecast, Location, Condition
from django.contrib.auth import get_user_model
from .serializers import ForecastSerializer, ConditionSerializer, LocationSerializer
from authentication.models import QueryHistory

User = get_user_model()

# Custom permission to check request limits
class RequestLimitPermission(BasePermission):
    message = 'You have reached the maximum number of requests for today. Upgrade to premium for unlimited requests.'
    
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            # Authenticated users (including premium) have no request limit
            return True

        # Anonymous users have a default limit
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key

        request_count = request.session.get('anonymous_request_count', 0)
        last_request_date_str = request.session.get('last_anonymous_request_date', '')

        today = date.today()
        if last_request_date_str != str(today):
            request.session['anonymous_request_count'] = 0
            request.session['last_anonymous_request_date'] = str(today)
            request_count = 0

        if request_count >= 10: #  10 is the limit for anonymous users
            self.message = 'You have reached the maximum number of requests for today. Please try again tomorrow.'
            return False

        request.session['anonymous_request_count'] = request_count + 1
        return True


# Custom decorator to check if user is the creator of the forecast
def user_is_forecast_creator(view_func):
    @wraps(view_func)
    def wrapper(request, forecast_id, *args, **kwargs):
        try:
            forecast = Forecast.objects.get(id=forecast_id)
        except Forecast.DoesNotExist:
            return Response({"error": "Forecast not found"}, status=HTTP_404_NOT_FOUND)
            
        if forecast.creator != request.user:
            return Response({"error": "You do not have permission to delete this forecast"}, status=HTTP_403_FORBIDDEN)
            
        return view_func(request, forecast_id, *args, **kwargs)
    return wrapper

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@user_is_forecast_creator
def delete_forecast(request, forecast_id):
    """Delete a forecast - only available to the creator of the forecast"""
    try:
        forecast = Forecast.objects.get(id=forecast_id)
        
        # The others get deleted automatically thanks to the on_delete=models.CASCADE
        forecast.delete()
        
        return Response({"message": "Forecast deleted successfully"}, status=HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@user_is_forecast_creator
def toggle_weather_alert(request, forecast_id):
    """Toggle the weather alert status for a forecast - only available to the creator of the forecast"""
    try:
        forecast = Forecast.objects.get(id=forecast_id)
        
        # Get the weather_alert value from the request data or toggle the current value
        if 'weather_alert' in request.data:
            forecast.weather_alert = request.data['weather_alert']
        else:
            forecast.weather_alert = not forecast.weather_alert
        
        forecast.save()
        
        return Response(ForecastSerializer(forecast).data, status=HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)

# function based view to get forecasts
@api_view(['GET'])
@permission_classes([IsAuthenticated, RequestLimitPermission])
def get_all_forecasts(request):
    user_filter = request.query_params.get('user')
    if user_filter:
        try:
            user = User.objects.get(username=user_filter)
            forecasts = Forecast.objects.filter(creator=user)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=HTTP_404_NOT_FOUND)
    else:
        forecasts = Forecast.objects.all()
    serializer = ForecastSerializer(forecasts, many=True)
    return Response(serializer.data)

# Class-based view using generics for listing forecasts with a slightly different order
class ForecastListView(generics.ListAPIView):
    serializer_class = ForecastSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date']
    ordering = ['-date']
    
    def get_queryset(self):
        queryset = Forecast.objects.all()
        username = self.request.query_params.get('user', None)
        if username is not None:
            try:
                user = User.objects.get(username=username)
                queryset = queryset.filter(creator=user)
            except User.DoesNotExist:
                queryset = Forecast.objects.none()
        return queryset

@api_view(['POST'])
@permission_classes([RequestLimitPermission])
def create_forecast(request):
    data = request.data
    user = request.user

    # Validate Location Data
    if not data.get('region') or not data.get('country'):
        return Response({"error": "Region and Country are required for Location."}, status=HTTP_400_BAD_REQUEST)

    location_data = {
        'region': data['region'],
        'country': data['country']
    }
    location_serializer = LocationSerializer(data=location_data)
    if location_serializer.is_valid():
        location = location_serializer.save()
    else:
        return Response(location_serializer.errors, status=HTTP_400_BAD_REQUEST)

    # Validate Condition Data
    required_condition_fields = ['condition', 'temperature', 'humidity', 'wind_speed', 'air_quality']
    missing_fields = [field for field in required_condition_fields if field not in data]
    if missing_fields:
        return Response({"error": f"Missing condition fields: {', '.join(missing_fields)}"}, status=HTTP_400_BAD_REQUEST)

    condition_data = {field: data[field] for field in required_condition_fields}
    condition_serializer = ConditionSerializer(data=condition_data)
    if condition_serializer.is_valid():
        condition = condition_serializer.save()
    else:
        return Response(condition_serializer.errors, status=HTTP_400_BAD_REQUEST)

    # Create Forecast
    forecast_data = {
        'location_id': location.id,
        'condition_id': condition.id,
        'weather_alert': data.get('weather_alert', False)
    }
    forecast_serializer = ForecastSerializer(data=forecast_data)
    if forecast_serializer.is_valid():
        if request.user.is_authenticated:
            forecast = forecast_serializer.save(creator=request.user)
        else:
            forecast = forecast_serializer.save(creator=None)
        
        # Save query history for premium users
        if request.user.is_authenticated and request.user.is_premium:
            QueryHistory.objects.create(
                user=user,
                region=location.region,
                country=location.country
            )
            
        return Response(ForecastSerializer(forecast).data, status=HTTP_201_CREATED)
    else:
        return Response(forecast_serializer.errors, status=HTTP_400_BAD_REQUEST)





