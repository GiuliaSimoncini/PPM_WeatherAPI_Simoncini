from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group
from .models import QueryHistory

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    is_premium = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'is_premium')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        is_premium = validated_data.pop('is_premium', False)
        validated_data.pop('password2')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_premium=is_premium
        )
        
        # Add user to appropriate group
        group_name = 'Premium' if is_premium else 'Anonymous'
        try:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
        except Group.DoesNotExist:
            # Create the group if it doesn't exist
            group = Group.objects.create(name=group_name)
            user.groups.add(group)
            
        return user

class QueryHistorySerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = QueryHistory
        fields = ['id', 'username', 'region', 'country', 'date']
        read_only_fields = ['id', 'date', 'username']
