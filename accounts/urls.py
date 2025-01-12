from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('login/steam/', views.steam_login, name='steam_login'),
    path('steam/callback/', views.steam_callback, name='steam_callback'),
    path('accounts/login/steam/success/', views.steam_login_success, name='steam_login_success'),
    path('accounts/steam/error/', views.steam_error, name='steam_error'),
    path('profile/', views.user_profile, name='user_profile'),
]