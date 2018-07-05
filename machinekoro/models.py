from django.db import models

# Create your models here.


class GameSession(models.Model):
    serial = models.IntegerField
    tracker = models.IntegerField
    channel_register = models.TextField #JSON
    # players foreign key'ed related_name = "players"


class Player_DB(models.Model):
    player_num = models.IntegerField
    name = models.CharField(max_length=32)
    mascot_code = models.IntegerField(blank=True)
    hand = models.TextField #JSON
    landmark = models.TextField #JSON
    coin = models.IntegerField
    game = models.ForeignKey('GameSession',related_name='players',on_delete=models.CASCADE)
