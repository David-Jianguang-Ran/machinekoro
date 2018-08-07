from django.contrib import admin
from django.db import models


class MatchSession(models.Model):
    """
    This object stores game state in components wit a match serial
    attributes:
    - game_id = string uuid # maybe i should change it to something more unique
    - register = text json {
        player_by_num:{
            token:
            player_num:
            is_prime:
            is_robot:
            channel_name:
            }
        }
    - tracker = text json {
         hand_count : int
         active_player : player.num
         phase : string
         }
    - market = text json Market obj in game_state.py
    - player_list = text json
    """
    match_id = models.CharField(max_length=40)
    in_progress = models.BooleanField()
    register = models.TextField()
    tracker = models.TextField()
    market = models.TextField()
    player_list = models.TextField()
    temp_data = models.TextField()


class TokenRegister(models.Model):
    """
    This object stores setting dicts with an uuid for MatchController to call on
    This is ONLY used to pass data to player to consumers
    attributes:
    - token = string
    - match_session = foreign key'ed to GameSession
    - content = json text data
        sample:
        register_entry = {
            'match_id': match_id uuid string
            'player_num': num int
            'is_prime': bool
            'is_bot': bool
            'self_channel_name' : consumer channel name (uuid?/string?)
        }
    """
    token = models.CharField(max_length=40)
    match_session = models.ForeignKey(MatchSession,verbose_name="session", on_delete=models.CASCADE)
    content = models.TextField()


class TreeSearchData(models.Model):
    """
    This object is used to store simulation data for the TreeSearchController
    All data is stored as json text field
    attributes:
    - plays = json text data
    - wins = json text data
    """
    label_options = [("na",'default')]

    label = models.CharField(max_length=20,choices=label_options)
    plays = models.TextField()
    wins = models.TextField()


# all models are registered here
admin.site.register(MatchSession)
admin.site.register(TokenRegister)
admin.site.register(TreeSearchData)




