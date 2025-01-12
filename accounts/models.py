from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  steam_id = models.CharField(max_length=100, unique=True)
  avatar_url = models.URLField(null=True, blank=True)
  display_name = models.CharField(max_length=100, null=True, blank=True)
  # 他に必要な情報はここ
  def __str__(self):
    return f"{self.user.username}'s profile"