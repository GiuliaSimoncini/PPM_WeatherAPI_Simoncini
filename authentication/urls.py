from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, QueryHistoryListView, UserProfileView, upgrade_to_premium

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('query-history/', QueryHistoryListView.as_view(), name='query_history'),
    path('upgrade/', upgrade_to_premium, name='upgrade_to_premium'),
]