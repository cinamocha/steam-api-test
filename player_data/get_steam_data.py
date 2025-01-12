import requests 
from .models import Game  # models.pyからGameモデルをインポート

STEAM_API_URL = 'https://api.steampowered.com/ISteamApps/GetAppList/v2/'

# Steam APIからゲームのリストを取得し、データベースに保存する
def fetch_and_store_steam_games():
  try:
    response = requests.get(STEAM_API_URL)
    response.raise_for_status() #エラーがあれば例外を発生させる
    data = response.json()
    
    games = data.get('applist', {}).get('apps', [])
    if not games:
      print('No games found')
      return
    
    for game in games:
      appid = game.get('appid')
      name = game.get('name' , 'Unknown')
      
      if appid and name:
        Game.objects.update_or_create(appid=appid, defaults={'name': name})
    
    print(f'Successfully stored {len(games)} games')
    
    stored_count = 0
    for game in games:
      appid = game.get('appid')
      name = game.get('name', 'Unknown')
      
      if appid and name:
        _, created = Game.objects.get_or_create(appid=appid, defaults={'name': name})
        if created:
          stored_count += 1
    print(f'New games stored: {stored_count}')
  
  except Exception as e:
    print(f'Error fetching and storing games: {e}')