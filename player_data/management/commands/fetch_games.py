from django.core.management.base import BaseCommand
from player_data.get_steam_data import fetch_and_store_steam_games

class Command(BaseCommand):
  help = 'Fetch and store games from the Steam API'

  def handle(self, *args, **kwargs):
    fetch_and_store_steam_games()