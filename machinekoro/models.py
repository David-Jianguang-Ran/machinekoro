from django.db import models

import uuid


class TokenRegister(models.Model):
    """
    This object stores setting dicts with an uuid for MatchController to call on
    attributes:
    - token = string
    - game_session = foreign key'ed to GameSession
    - content = json string
    """
    token = models.CharField(max_length=40)
    content = models.TextField()


class GameSession(models.Model):
    """
    This object stores game state with a tracker object and a gamesession serial
    attributes:
    - game_id = string uuid # maybe i should change it to something more unique
    - tracker = text json {
         hand_count : int
         active_player : player.num
         phase : string
         }
    - player_list = text json
    """
    game_id = models.CharField(max_length=40)
    tracker = models.TextField()
    player_list = models.TextField()
