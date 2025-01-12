from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import requests
import os
from dotenv import load_dotenv
from .models import Game
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from functools import wraps
import time
from django.shortcuts import get_object_or_404
from accounts.models import UserProfile
from django.urls import reverse

def get_steam_api_key():
  load_dotenv()
  return os.getenv('STEAM_API_KEY')

def get_owned_games(steam_id):
  api_key = get_steam_api_key()
  url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={api_key}&steamid={steam_id}&include_appinfo=true'
  
  try:
    response = requests.get(url)
    response.raise_for_status()
    game_data = response.json().get('response', {}).get('games', [])
    return game_data  # ゲームのリストを返す
  except requests.exceptions.RequestException as e:
    print(f"Error fetching owned games: {e}")
    return []

def owned_games_list(request, steam_id):
  owned_games = get_owned_games(steam_id)
    
  if not owned_games:
    return render(request, 'player_data/owned_games_list.html', {'error': '所有しているゲームがありません。'})

  return render(request, 'player_data/owned_games_list.html', {
    'owned_games': owned_games,
    'steam_id': steam_id
  })

def player_profile(request):
  print('player_profileが呼び出されました')
  steam_id = request.GET.get('steam_id')
  
  if not steam_id:
    return render(request, 'player_data/player_profile.html', {'error': 'Steam IDを入力してください。'})
  
  api_key = get_steam_api_key()
  url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={api_key}&steamids={steam_id}'
  
  try:
    response = requests.get(url)
    response.raise_for_status()
    play_data = response.json()
    play_info = play_data.get('response' , {}).get('players' , [])
    
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    user_profile.steam_id = steam_id
    user_profile.save()

    if not play_info:
      return render(request, 'player_data/player_profile.html', {'error': 'プレイヤー情報が見つかりませんでした。'})

    owned_games = get_owned_games(steam_id)
    
    if steam_id:
      player_time_url = reverse('player_time', kwargs={'steam_id': steam_id})
      achievement_list_url = reverse('achievement_list', kwargs={'steam_id': steam_id, 'appid': 0})
    else:
      player_time_url = None
      achievement_list_url = None
    
    return render(request, 'player_data/player_profile.html', {
      'play_info': play_info[0],
      'player_time_url': player_time_url,
      'owned_games': owned_games,
      'steam_id': steam_id,
      #'achievement_list_url': reverse('achievement_list', kwargs={'steam_id': steam_id , 'appid': appid}),
      #'achievement_details_url': reverse('achievement_details', kwargs={'steam_id': steam_id})
    })
    
  except requests.exceptions.RequestException as e:
    return render(request, 'player_data/player_profile.html', {'error': 'エラーが発生しました。'})

def rate_limit(calls=1, period=1):
  def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
      cache_key = f'ratelimit_{func.__name__}'
      calls_history = cache.get(cache_key, [])
      
      now = time.time()
      calls_history = [t for t in calls_history if now - t < period]
      
      if len(calls_history) >= calls:
        raise Exception('Rate limit exceeded')
      
      calls_history.append(now)
      cache.set(cache_key, calls_history, timeout=period)
      
      return func(*args, **kwargs)
    return wrapper
  return decorator

@rate_limit(calls=1000, period=60)
def get_game_name(appid):
  try:
    game = Game.objects.get(appid=appid)
    return game.name
  except Game.DoesNotExist:
    return 'Unknown'
  
  try:
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
    response = requests.get(url)
    data = response.json()
    
    if not data or str(appid) not in data:
      print(f'No data for appid {appid}')
      return 'Unknown'
    
    app_data = data[str(appid)]
    
    if app_data.get('success') and 'data' in app_data:
      return app_data['data'].get('name', 'Unknown')
  except Exception as e:
    print(f'Error fetching name for {appid}:{e}')
    return 'Unknown'


def player_time(request, steam_id):
  print(f'Steam ID: {steam_id}')
  #steam_id = request.GET.get('steam_id')
  print(f"Steam ID: {steam_id}")
  if not steam_id:
    return HttpResponse('Steam IDが設定されていません。')
  
  api_key = get_steam_api_key()
  url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steam_id}&format=json'
  
  try:
    response = requests.get(url)
    print(f"Response status code: {response.status_code}")
    response.raise_for_status()
    
    if 'Rate limit exceeded' in response.text:
      return HttpResponse('リクエストの制限を超えました。')
    
    play_data = response.json()
    
    game_info = []
    
    if 'response' in play_data and 'games' in play_data['response']:
      total_playtime = sum(game.get('playtime_forever', 0) for game in play_data['response']['games'])
      threshold = total_playtime * 0.01
      
      other_playtime = 0
      filtered_game_info = []
      
      for game in play_data['response']['games']:
        appid = game.get('appid')
        if appid is None:
          continue
        
        playtime_forever = game['playtime_forever']
        game_name = get_game_name(appid)
        playtime = game.get('playtime_forever', 0)
        
        if playtime >= threshold:
          filtered_game_info.append({'name': game_name, 'playtime': playtime // 60})
        else:
          other_playtime += playtime
      
      if other_playtime > 0:
        filtered_game_info.append({'name': 'その他', 'playtime': other_playtime // 60})
    
    print(f'game_info: {game_info}')
    
    game_names = [game['name'] for game in game_info]
    play_times = [game['playtime'] for game in game_info]
    
    fig, ax = plt.subplots()
    ax.pie(play_times, labels=game_names, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    
    game_info.sort(key=lambda x: x['playtime'], reverse=True)
    
    return render(request, 'player_data/player_time.html', {'game_info': filtered_game_info, 'total_playtime': total_playtime, 'img_base64': img_base64})
  
  except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    return HttpResponse('エラーが発生しました。')
  except Exception as e:
    if 'Rate limit exceeded' in str(e):
      return HttpResponse('リクエストの制限を超えました。')
    print(f"Unexpected error: {e}")
    return HttpResponse('予期しないエラーが発生しました。')

def achievement_list(request, steam_id, appid):
  if not steam_id:
    return HttpResponse('Steam IDが設定されていません。')
  
  api_key = get_steam_api_key()
  
  # プレイヤーが所有しているゲームリストを取得
  games_url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steam_id}&format=json'
  try:
    response = requests.get(games_url)
    response.raise_for_status()
    games_data = response.json()
    games = games_data.get('response', {}).get('games', [])
    achievements = get_achievement_details(steam_id, appid)
    print(f"Achievements: {achievements}")  # デバッグ用
    
    # ゲームのapp_idと名前を渡す
    game_info = [{'appid': game['appid'], 'name': game['name']} for game in games]
    
    return render(request, 'player_data/achievement_list.html', {
      'steam_id': steam_id,
      'appid': appid,
      'achievements': achievements,
      'games': game_info
    })
  
  except requests.exceptions.RequestException as e:
    return HttpResponse('エラーが発生しました。')

#実績の詳細の取得
def get_achievement_details(steam_id, appid):
  api_key = get_steam_api_key()
  
  schema_url = f"http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/"
  param = {'appid': appid, 'key': api_key}
  schema_response = requests.get(schema_url, params=param)
  
  if schema_response.status_code != 200:
    print(f"Failed to fetch schema, status code: {schema_response.status_code}")
    return []
  
  schema_data = schema_response.json()
  all_achievements = schema_data.get('game', {}).get('availableGameStats', {}).get('achievements', [])
  
  url = f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/"
  achievements_params = {'steamid': steam_id, 'appid': appid, 'key': api_key}
  
  response = requests.get(url, params=achievements_params)
  
  if response.status_code != 200:
    print(f"Failed to fetch achievements, status code: {response.status_code}")
    return []
  
  achievements = response.json().get('playerstats', {}).get('achievements', [])
  achieved_names = {a.get('apiname') for a in achievements if a.get('achieved') == 1}
  
  filtered_achievements = [
    {
      'apiname': achievement.get('name'),
      'displayName': achievement.get('displayName', 'Unknown')
    }
    for achievement in all_achievements
    if achievement.get('name') in achieved_names
  ]
  return filtered_achievements

def get_schema_details(appid):
  api_key = get_steam_api_key()
  url = f"http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/"
  params = {'appid': appid, 'key': api_key}

  response = requests.get(url, params=params)
  
  if response.status_code == 200:
    return response.json()
  else:
    print(f"スキーマの取得に失敗: {response.text}")
    return {}

def get_achievements(request, steam_id, appid):
  
  print(f"Steam ID: {steam_id}, App ID: {appid}") # デバッグ用
  
  if not steam_id or not appid:
    return JsonResponse({'error': '不正なパラメータが指定されました。'})

  achievements = get_achievement_details(steam_id, appid)
  #print(f"Achievements: {achievements}") # デバッグ用
  
  if not achievements:
    return JsonResponse({'achievements': []})
  
  schema_response = get_schema_details(appid)
  all_achievements = schema_response.get('game', {}).get('availableGameStats', {}).get('achievements', [])
  
  achievements_data = []
  for achievement in achievements:
    if achievement.get('achieved') == 1:
      display_name = next((ach['displayName'] for ach in all_achievements if ach['name'] == achievement['apiname']), "Unknown")
      achievements_data.append({'apiname': achievement['apiname'], 'name': display_name})

  return JsonResponse({'achievements': achievements_data})


#def achievement_details(request, steam_id):
  print(f'Steam ID: {steam_id}')
  
  if not steam_id:
    return HttpResponse('Steam IDが設定されていません。')
  
  try:
    # 実績データを取得
    achievements = get_achievement_details(steam_id)
    total_achievements = len(achievements)
    
    # 実績詳細を返す
    return render(request, 'player_data/achievement_details.html', {
      'achievements': achievements,
      'total_achievements': total_achievements,
      'steam_id': steam_id
    })
    
  except requests.exceptions.RequestException as e:
    # リクエストエラーが発生した場合
    print(f"Error fetching achievements: {e}")
    return HttpResponse(f"Error: {e}")
  except ValueError:
    # JSONパースエラーが発生した場合
    print("Error parsing JSON response")
    return HttpResponse("Error parsing response")
