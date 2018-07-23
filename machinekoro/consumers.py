from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import SyncConsumer, AsyncJsonWebsocketConsumer

import asyncio
import copy
import json

from . import views
from . import controllers


class PlayerWSConsumer(AsyncJsonWebsocketConsumer):
    """
    This Consumer handles ws connection from client. It is instanciated once per connection
    O attributes:
    - register = {
    match_id : uuid string
    player_num = int num 1-5
    is_prime : bool
    is_bot : bool
    prime_player_channel: channel_name
    }
    - register_prime = [ of all register obj from all player ]

    methods callable by channels:

    - send_json

    - prime_register_update

    - new_query_set

    methods callable by client:

    - prime_player_command

    methods available only to prime player:


    """
    async def connect(self):
        """
        This method is called on connection with ws
        It takes the token from url, gets a register obj and copies it to memory
        it also updates the token record with new channel name
        :return: None
        """
        # call game controller function to retrieve content
        token = self.scope['url_route']['kwargs']['token']
        register_content = sync_to_async(controllers.MatchController.initialize_by_token(token,self.channel_name))

        self.register = register_content
        match_id = self.register['match_id']

        await self.accept()
        await self.channel_layer.group_add(match_id)
        pass

    async def prime_register_update(self,event):
        """
        this method receives updates of prime_register obj send from MatchController.add_player_to_match
        if the player is prime, then the prime_register gets saved
        then prime_register gets forwarded to client with key register_update
        :param event: event obj from channels
        :return:
        """
        content = event['content']

        # prime player consumer keeps the whole register in memory for routing
        if self.register['is_prime']:
            self.register_prime = content

        # forward update to client withe the appropriate key
        client_massage = {
            "key": "register_update",
            "content": content
        }
        await self.send_json(client_massage)

    async def prime_player_command(self, message):
        """
        This methods handles all client prime player command
        functions are called based on key of the client message:
            "start_game" : send process request to GameProcessor
            "add_bot" : add bot player register using MatchController
        :param message: msg with key "prime.player.command"
        :return:
        """
        key = message['key']
        if key == "start_game" and self.register['is_prime']:
            # send channel_layer initial turn process request msg to GameProcessor
            pass
        elif key == "add_bot" and self.register['is_prime']:
            match_id = self.register['match_id']
            none_value = sync_to_async(controllers.MatchController.add_player_to_match(match_id,prime=False,bot=True))
        else:
            print(str(self.__doc__)+"prime command ignored key="+key)
        pass

    async def disconnect(self, code):
        if self.register['is_prime']:
            pass
        else:
            pass

    async def receive_json(self, content, **kwargs):
        """
        This method takes message from ws connection (client) and routes based on type
        :param content:
        :param kwargs:
        :return:
        """
        if content['type'] == 'prime.player.command':
            await self.prime_player_command(content)
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
        """
        This method is called by channel layer with key 'initial.turn'
        This method takes the match_id, creates state, saves to db then sends the queries
        needed to advance the state to player prime
        :param event: {
            "type": 'initial.turn',
            "prime_channel_name": channel name,
            "match_id": uuid string
        }
        :return: sends query message to player prime
        """
        match_id = event['match_id']
        prime_channel_name = event['prime_channel_name']
        game_controller = controllers.GameController(match_id=match_id)

        sync_to_async(game_controller.initialize_state())
        query_set = sync_to_async(game_controller.get_query_set())

        message = {
            "type": "process_query_set",
            "match_id": match_id,
            "query_set": query_set
        }

        await self.channel_layer.send(prime_channel_name, message)

    async def get_query_set(self,event):
        """
        This method is called by channel layer with key 'get.query.set'
        This method takes the match_id, loads state, makes query_set then sends the queries
        needed to advance the state to player prime
        :param event: {
            "type": 'get.query.set',
            "prime_channel_name": channel name,
            "match_id": uuid string
        }
        :return: sends query message to player prime
        """
        match_id = event['match_id']
        prime_channel_name = event['prime_channel_name']
        game_controller = controllers.GameController(match_id=match_id)

        query_set = sync_to_async(game_controller.get_query_set())

        message = {
            "type":"process_query_set",
            "match_id": match_id,
            "query_set":query_set
        }

        await self.channel_layer.send(prime_channel_name, message)

    async def process_response(self,event):
        """
        This method is called by channel layer with key 'process.response'
        This methods applies all game state modifications in response_set, saves to db
        then sends a confirmation message back to player prime
        :param event: {
            "type": 'process.response',
            "prime_channel_name": channel name,
            "match_id": uuid string,
            "response_set": response_set obj
        }
        :return: sends channel layer message to player prime
        """
        match_id = str(event['match_id'])
        prime_channel_name = event['prime_channel_name']
        response_set = event['response_set']
        game_controller = controllers.GameController(match_id=match_id)

        sync_to_async(game_controller.process_query_response(response_set))

        message = {
            "type":"process_response_complete",
            "match_id": match_id
        }

        await self.channel_layer.send(prime_channel_name, message)


class BotProcessorConsumer(SyncConsumer):
    """
    This consumer handles decision request from player prime.
    This object is stateless, all game state data comes from db lookup

    methods callable by channels:

    - respond_query

    """
    async def respond_query(self,event):
        pass
