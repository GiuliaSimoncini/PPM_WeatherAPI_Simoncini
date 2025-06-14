from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser.
    This allows to add fields and customization.
    """
    # Add custom fields
    is_premium = models.BooleanField(default=False)
    daily_request_count = models.IntegerField(default=0)
    last_request_date = models.DateField(null=True, blank=True)
    
    # Add related_name to avoid clashes with auth.User
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='customuser_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='customuser_set',
        related_query_name='user',
    )
    
    def __str__(self):
        return self.username

class QueryHistory(models.Model):
    """
    Model to store query history for premium users.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='query_history')
    region = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.region}, {self.country} - {self.date}"
    
    class Meta:
        verbose_name_plural = "Query histories"
        ordering = ['-date']  # Most recent queries first
