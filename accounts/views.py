from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from openid.consumer.consumer import Consumer, SUCCESS
from openid.store.memstore import MemoryStore
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from .models import UserProfile
from player_data.views import player_profile, player_time
from dotenv import load_dotenv
import os

api_key = os.getenv('STEAM_API_KEY')

#ログインビュー
def login_view(request):
  if request.method == 'POST':
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
      login(request, user)
      return redirect('/')  #ログイン後にリダイレクト
    else:
      return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
  return render(request, 'accounts/login.html')

#ログアウトビュー
def logout_view(request):
  logout(request)
  return redirect('/')

#サインアップビュー
def signup_view(request):
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect('login')
  else:
    form = UserCreationForm()
  return render(request, 'accounts/signup.html', {'form': form})

def steam_login(request):
  try:
    #SteamOpenIDエンドポイント
    steam_openid_url = 'https://steamcommunity.com/openid'
    consumer = Consumer({}, MemoryStore())

    #Steam認証用リクエストを作成
    auth_request = consumer.begin(steam_openid_url)

    if auth_request is None:
      messages.error(request, "Steam認証の開始に失敗しました")
      return redirect('home')  #エラー処理

    trust_root = settings.SITE_URL
    return_to = f'{trust_root}accounts/steam/callback'
    redirect_url = auth_request.redirectURL(trust_root, return_to=return_to)

    request.session['steam_auth_request'] = str(auth_request)  #セッションに保存
    return redirect(redirect_url)
  except Exception as e:
    messages.error(request, f"エラーが発生しました: {str(e)}")
    return redirect('home')


def steam_callback(request):
  try:
    consumer = Consumer(request.session, MemoryStore())

    query_dict = request.GET
    openid_response = consumer.complete(query_dict, request.build_absolute_uri())

    if openid_response.status == SUCCESS:
      steam_id = openid_response.getDisplayIdentifier().split('/')[-1]  #SteamIDを取得
      return steam_login_success(request, steam_id)
    else:
      return redirect('home')
  except Exception as e:
    messages.error(request, f"エラーが発生しました: {str(e)}")
    return redirect('home')

def steam_login_success(request, steam_id):
  try:
    #ユーザーの取得または新規作成
    user, created = User.objects.get_or_create(username=f'steam_{steam_id}')
    
    #UserProfileの取得または新規作成
    user_profile, profile_created = UserProfile.objects.get_or_create(user=user)
    
    #SteamIDをユーザーのプロフィールに設定
    user_profile.steam_id = steam_id
    user_profile.save()
    
    #ログイン処理
    login(request, user)
    
    #メッセージを追加（成功時）
    if created or profile_created:
      messages.success(request, "Steamアカウントでログインしました！")
    
    #プレイヤープロフィールページにリダイレクト
    return redirect('player_profile')
    
  except ObjectDoesNotExist:
    #ユーザーが存在しない場合のエラーハンドリング
    messages.error(request, "Steamアカウントが見つかりませんでした。再度お試しください。")
    return redirect('signup')
    
  except Exception as e:
    #その他のエラーが発生した場合のエラーハンドリング
    messages.error(request, f"エラーが発生しました: {e}")
    return redirect('signup')


def steam_error(request):
  return render(request, 'error.html')

def user_profile(request):
  try:
    user_profile = UserProfile.objects.get(user=request.user)
    profile_data = get_steam_user_profile(user_profile.steam_id)
    return render(request, 'player_profile.html', {'profile_data': profile_data})
  except UserProfile.DoesNotExist:
    messages.error(request, "プロフィールが見つかりませんでした。")
    return redirect('home')
