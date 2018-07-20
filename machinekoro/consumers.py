from asgiref.sync import async_to_sync,sync_to_async
from channels.generic.websocket import SyncConsumer,AsyncConsumer,AsyncJsonWebsocketConsumer

import asyncio
import copy
import json

from . import views
from . import controllers


class PlayerWSConsumer(AsyncJsonWebsocketConsumer):
    """
    This Consumer handles ws connection from client. It is instanciated once per connection
    attributes:
    - context = {
    is_prime_player : bool
    prime_player_channel: channel_name
    }

    methods callable by channels:


    methods callable by client:


    methods available only to prime player:


    """
    async def connect(self):
        pass

    async def disconnect(self, code):
        pass

    async def send_json(self, content, close=False):
        pass

    async def receive_json(self, content, **kwargs):
        pass


class GameProcessorConsumer(SyncConsumer):
    """
    This consumer handles game process requests from player prime.
    This object is stateless, all game state data comes from db lookup

    methods callable by channels:

    - initial_turn

    - get_query_set

    - process_response

    """
    async def initial_turn(self,event):
        pass

    async def get_query_set(self,event):
        pass

    async def process_response(self,event):
        pass


class BotProcessorConsumer(SyncConsumer):
    """
    This consumer handles decision request from player prime.
    This object is stateless, all game state data comes from db lookup

    methods callable by channels:

    - respond_query

    """
    async def respond_query(self,event):
        pass