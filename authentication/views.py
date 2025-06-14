from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.conf import settings
from .serializers import RegisterSerializer, QueryHistorySerializer
from .models import QueryHistory

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class QueryHistoryListView(generics.ListAPIView):
    serializer_class = QueryHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only premium users can access their query history
        if self.request.user.is_premium:
            return QueryHistory.objects.filter(user=self.request.user)
        return QueryHistory.objects.none()

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'email': user.email,
            'is_premium': user.is_premium,
            'daily_request_count': user.daily_request_count,
            'last_request_date': user.last_request_date,
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upgrade_to_premium(request):
    user = request.user
    if user.is_premium:
        return Response({'message': 'User is already a premium user'}, status=status.HTTP_400_BAD_REQUEST)

    user.is_premium = True
    user.save()
    
    # Add user to Premium group
    from django.contrib.auth.models import Group
    premium_group, _ = Group.objects.get_or_create(name=settings.PREMIUM_GROUP)
    user.groups.add(premium_group)
    
    # Remove from Anonymous group if they were in it
    try:
        anonymous_group = Group.objects.get(name=settings.ANONYMOUS_GROUP)
        user.groups.remove(anonymous_group)
    except Group.DoesNotExist:
        pass
    
    return Response({'message': 'Successfully upgraded to premium'}, status=status.HTTP_200_OK)