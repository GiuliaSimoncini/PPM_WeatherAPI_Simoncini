from rest_framework import serializers
from .models import Forecast, Condition, Location

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'region', 'country']
        read_only_fields = ['id']

class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = ['id', 'condition', 'temperature', 'humidity', 'wind_speed', 'air_quality']
        read_only_fields = ['id']

class ForecastSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.username')
    location = LocationSerializer(read_only=True)
    condition = ConditionSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), write_only=True, source='location'
    )
    condition_id = serializers.PrimaryKeyRelatedField(
        queryset=Condition.objects.all(), write_only=True, source='condition'
    )
    class Meta:
        model = Forecast
        fields = [
            'id',
            'location',         # nested output
            'location_id',      # id input
            'condition',        # nested output
            'condition_id',     # id input
            'date',
            'weather_alert',
            'creator'
        ]
        read_only_fields = ['id', 'date', 'creator']
