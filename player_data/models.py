from django.db import models

class Game(models.Model):
  appid = models.IntegerField(unique=True , db_index=True)
  name = models.CharField(max_length=255)
  
  def __str__(self):
    return self.name
