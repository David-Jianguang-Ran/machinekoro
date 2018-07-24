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
    prime_player_channel: channel_name # um.... not happening
    }
    - register_prime = [ of all register obj from all player ]

    methods callable by channels :

    - register_update


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

        # copy register to memory
        self.register = register_content

        match_id = self.register['match_id']

        await self.accept()
        await self.channel_layer.group_add(match_id)
        pass

    async def register_update(self,event):
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

        # forward update to client with the appropriate key
        # note that all clients would keep the prime_register for match player data to name or whatever (.......)
        client_massage = {
            "key": "register_update",
            "content": content
        }
        await self.send_json(client_massage)

    async def game_state_update(self,event):
        """
        This method is called by a broadcast message into group from GameProcessor
        :param event: looks something like this:
            message = {
            "type": "game.state.update",
            "match_id":self.match_id ,
            "content": json_set = {
                tracker:
                market :
                players :
            }
        }
        channel_laye
        :return:
        """
        pass

    async def prime_player_command(self, message):
        """
        This methods handles all client prime player command
        functions are called based on key of the client message:
            "start_game" : send process request to GameProcessor
            "add_bot" : add bot player register using MatchController
            "kick_player" : not implemented yet
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

    async def process_response_complete(self,event):
        """
        This method is called by GameProcessor via Channels when processing is complete
        Call next get query set here
        :param event:
        :return:
        """
        pass

    async def prime_process_query_set(self,event):
        """
        This method is called by a GameProcessor message with the key process.query.set (sent by get_query_set)
        This method:
            - takes the query set
            - computes query_set_snippet
            - looks up prime_register and sends query to players
            - block until complete
            - send response set to GameProcessor
        :param event: looks something like this:
            message = {
            "type":"process_query_set",
            "match_id": match_id,
            "query_set":query_set
        }
        :return:
        """
        pass

    async def prime_send_query_set_request(self):
        if self.register['is_prime']:
            message = {
                "type" : "get.query.set",
                "prime_channel_name" : self.channel_name,
                "match_id" : self.register['match_id']
            }
            await self.channel_layer.send("GamProcessor",message)
        else:
            print("prime Player methods can only be called by prime player")

    async def prime_send_response_process_request(self,response_set):
        if self.register['is_prime']:
            message = {
                "type" : "process.response",
                "prime_channel_name" : self.channel_name,
                "match_id" : self.register['match_id'],
                "response_set" : response_set
            }
            await self.channel_layer.send("GamProcessor",message)
        else:
            print("prime Player methods can only be called by prime player")

    async def disconnect(self, code):
        # remember to implement the switch prime thing
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
     > This is obj is all synchronous, you dummy! <
    methods callable by channels:

    - initial_turn

    - get_query_set

    - process_response

    """

    def initial_turn(self,event):
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

        game_controller.initialize_state()
        query_set = game_controller.get_query_set()

        message = {
            "type": "process_query_set",
            "match_id": match_id,
            "query_set": query_set
        }

        async_to_sync(self.channel_layer.send(prime_channel_name, message))

    def get_query_set(self,event):
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

        query_set = game_controller.get_query_set()

        message = {
            "type":"process_query_set",
            "match_id": match_id,
            "query_set":query_set
        }

        async_to_sync(self.channel_layer.send(prime_channel_name, message))

    def process_response(self,event):
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

        game_controller.process_query_response(response_set)

        message = {
            "type":"process.response.complete",
            "match_id": match_id
        }

        async_to_sync(self.channel_layer.send(prime_channel_name, message))


class BotProcessorConsumer(SyncConsumer):
    """
    This consumer handles decision request from player prime.
    This object is stateless, all game state data comes from db lookup

    methods callable by channels:

    - respond_query

    """
    async def respond_query(self,event):
        pass
