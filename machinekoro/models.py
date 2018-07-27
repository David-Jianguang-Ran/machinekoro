from django.db import models


class TokenRegister(models.Model):
    """
    This object stores setting dicts with an uuid for MatchController to call on
    This is ONLY used to pass data to player to consumers, not a player register
    attributes:
    - token = string
    - match_session = foreign key'ed to GameSession
    - content = json string
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
    match_session = models.ForeignKey(MatchSession, on_delete=models.CASCADE)
    content = models.TextField()


class MatchSession(models.Model):
    """
    This object stores game state with a tracker object and a match serial
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
    register = models.TextField()
    tracker = models.TextField()
    market = models.TextField()
    player_list = models.TextField()
