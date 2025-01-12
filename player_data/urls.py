from django.urls import path
from . import views

urlpatterns = [
  path('profile/', views.player_profile, name='player_profile'),
  path('player_time/<str:steam_id>/', views.player_time, name='player_time'),
  path('achievement_list/<str:steam_id>/<int:appid>/', views.achievement_list, name='achievement_list'),
  path('owned_games/<str:steam_id>/', views.owned_games_list, name='owned_games_list'),
  path('get_achievements/<str:steam_id>/<int:appid>/', views.get_achievements, name='get_achievements'),
]