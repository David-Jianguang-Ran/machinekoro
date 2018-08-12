from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import SyncConsumer, AsyncJsonWebsocketConsumer

import asyncio
import json

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
    channel_name: channel_name # um.... not happening
    }
    - register_prime = { of all register obj from all player }

    O methods callable by channels :

    - register_update

    - game_state_update

    - send_query_to_client

    - prime_process_response_complete

    - prime_process_query_set

    - prime_send_query_set_request

    - prime_send_response_process_request

    O methods callable by client:

    - prime_player_command

    - process_client_response

    methods available only to prime player:


    """
    async def connect(self):
        """
        This method is called on connection with ws
        It takes the token from url, gets a register obj and copies it to memory
        it also updates the token record with new channel name
        :return: None
        """
        # initialize some vars
        self.register = None
        self.register_prime = None
        self.query_routing_data = None

        # call game controller function to retrieve content
        token = self.scope['url_route']['kwargs']['token']
        register_content = await sync_to_async(controllers.MatchController.initialize_by_token)(token,self.channel_name)

        # copy register to memory
        self.register = register_content
        controllers.silly_print("PlayerConsumer init with the following register content",register_content)

        match_id = self.register['match_id']

        await self.accept()
        await self.channel_layer.group_add(match_id,self.channel_name)
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

        # forward update to client with the appropriate key
        # note that all clients would keep the prime_register for match player data to name or whatever (.......)
        client_massage = {
            "key": "register_update",
            "content": content
        }
        await self.send_json(client_massage)


#    async def game_state_update(self,event):
#        """
#        This method is called by a broadcast message into group from GameProcessor
#        :param event: looks something like this:
#            event = {
#           "type": "game.state.update",
#            "match_id":self.match_id ,
#            "content": json_set = {
#                tracker:
#                   market :
#                players :
#            }
#        }
#        channel_laye
#        :return:
#        """
#        event['key'] = "game_state_update"
#        await self.send_json(json.dumps(event))
#
#    async def dice_roll_update(self,event):
#        event['key'] = "dice_roll_update"
#        await self.send_json(event)

    async def send_message_to_client(self, event):
        """

        :param event:
        :return:
        """
        # loop up vars

        message = {
            "key":event['key'],
            "body": event['content']
        }

        controllers.silly_print("ws message sent to client",message)
        await self.send_json(message)

    async def send_query_set_to_client(self, event):
        """
        This method send query to client over ws
        :param event:
        :return:
        """
        # make sure client is getting a list of queries, even if there is only one
        query_set = event['query_set']
        if not type(query_set) == 'list':
            query_set = [query_set]

        query_json = json.dumps(query_set)
        await self.send_json(query_json)

    async def process_client_response(self, event):
        """
        This method could be called by both client and client consumer message
        for prime player, response is recorded and snippet compared to see if there is message outstanding
        for regular player, response is forwarded to prime with the correct type to call this function there
        :param event:
        :return:
        """
        if self.register['is_prime']:
            store = self.query_routing_data
            # add response to self.response_set
            response = event['response']
            store.response_set.append(response)

            # compute response_snippet
            response_set_snippet = []
            for each_response in store.response_set:
                num = each_response['player_num']
                q_type = each_response['q_type']
                response_set_snippet.append({num: q_type})

            if response_set_snippet == store.query_set_snippet:
                store.has_client_query_outstanding = False

        else:
            # look up prime channel name
            prime_channel = None
            for key in self.register_prime:
                if self.register_prime[key]['is_prime']:
                    prime_channel = self.register_prime[key]['channel_name']

            message = {
                "type": "process.client.response",
                "response": event['response']
            }

            await self.channel_layer.send(prime_channel, message)

    async def prime_process_response_complete(self,event):
        """
        This method is called by GameProcessor via Channels when processing is complete
        Call next get query set here
        :param event:
        :return:
        """
        await self.prime_send_query_set_request()

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
            query = {
        'key': "action.query",
        "player_num": 'player.num',
        "q_type": "invest_query",
        "options": [True, False],
        "only_option":'bool'
        }
        :return:
        """
        query_set = event['query_set']
        routing_data = self.query_routing_data
        routing_data.outgoing_query_sets = {}
        routing_data.query_set_snippet = []
        routing_data.has_client_query_outstanding = True
        routing_data.response_set = []

        # process each query in to query set to client
        for query in query_set:

            num = query['player_num']
            q_type = query['q_type']

            routing_data.query_set_snippet.append({num: q_type})

            if query['only_option'] and self.register_prime[num]['is_bot']:
                # if query has only one option going to a bot, add response automatically
                query['choice'] = query['options']
                event = {
                    "dummy_type":"kaka",  # this message isn't sent over channels, its just made to look like it
                    "response":query
                }
                await self.process_client_response(event)
            else:
                # append query to outgoing set with the co-responding player num
                routing_data.outgoing_query_sets[num].append(query)

        # send all query set channel message to clients
        for num in routing_data.outgoing_query_sets:
            player_register_data = self.register_prime[num]

            if player_register_data['is_bot']:
                # if player is bot, send processing request to botprocessor
                message = {
                    "type":"respond.query",
                    "prime_channel_name":self.channel_name,
                    "match_id":player_register_data['match_id'],
                    "player_num":num,
                    "query_set":routing_data.outgoing_query_sets[num]
                }
                await self.channel_layer.send("bot_processor",message)
            else:
                # send to consumer and to client
                # can i just send to self with channel_name? i guess yes, we'll see
                message = {
                    'type':"send.query.set.to.client",
                    'query_set': routing_data.outgoing_query_sets[num]
                }
                await self.channel_layer.send(player_register_data['channel_name'], message)

        # block until all response are in
        await self.__block_until_false(routing_data.has_client_query_outstanding)

        # make response message to game processor
        message = {
            "type": "process.response",
            "prime_channel_name": self.channel_name,
            "match_id": self.register['match_id'],
            "response_set":routing_data.response_set
        }
        await self.channel_layer.send("GamProcessor", message)

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
        cmd = message['cmd']

        if cmd == "start_game" and self.register['is_prime']:
            # send channel_layer initial turn process request msg to GameProcessor
            message = {
                "type":"initial.turn",
                "match_id": self.register['match_id'],
                "prime_channel_name": self.channel_name
            }
            await self.channel_layer.send("game_processor",message)

        elif cmd == "add_bot" and self.register['is_prime']:
            # add a bot player to match register,
            # note the bot player has no consumer actions are handled by prime
            match_id = self.register['match_id']
            none_value = await sync_to_async\
                (controllers.MatchController.add_player_to_match)\
                (controllers.MatchController(),match_id,prime=False,bot=True)
            controllers.silly_print("bot player added to game",self.register['match_id'])

        elif cmd == "kick_player" and self.register['is_prime']:
            # kick player from game and replace them with a bot
            target_player = message['target']
            target_register = self.register_prime[target_player]

            controllers.silly_print("kicking player from game, num = ",target_player)

            message = {
                "type":"send.message.to.client",
                "key":"alert",
                "content": "You have been removed from the game and replaced by bot"
            }

            await sync_to_async(controllers.MatchController.handle_player_disconnect)(target_register)
            await self.channel_layer.group_discard(self.register['match_id'], target_register['self_channel_name'])
            await self.channel_layer.send(target_register['self_channel_name'],message)

        else:
            print(str(self.__doc__)+"prime command ignored key="+cmd)
        pass

    async def prime_send_query_set_request(self):
        """
        This method sends a message to GameProcessor, instructing it to prepare a query_set and send them over channels
        :return:
        """
        if self.register['is_prime']:
            message = {
                "type" : "get.query.set",
                "prime_channel_name" : self.channel_name,
                "match_id" : self.register['match_id']
            }
            await self.channel_layer.send("game_processor",message)
        else:
            print("prime Player methods can only be called by prime player")

    async def prime_send_response_process_request(self,response_set):
        """
        This method sends a response_set to GameProcessor to modify gamestate based on the response
        All response must be in one set!
        :param response_set:
        :return:
        """
        if self.register['is_prime']:
            message = {
                "type" : "process.response",
                "prime_channel_name" : self.channel_name,
                "match_id" : self.register['match_id'],
                "response_set" : response_set
            }
            await self.channel_layer.send("game_processor",message)
        else:
            print("prime Player methods can only be called by prime player")

    async def disconnect(self, code):
        # Match controller will turn this player into a bot player, if this player is prime, another will be selected
        # then a update message will be sent to the remaining players
        await sync_to_async(controllers.MatchController.handle_player_disconnect)(self.register)
        await self.channel_layer.group_discard(self.register['match_id'],self.channel_name)

    async def receive_json(self, message, **kwargs):
        """
        This method takes message from ws connection (client) and routes based on type
        :param content:
        :param kwargs:
        :return:
        """
        # debug print incoming message from client
        controllers.silly_print("incoming ws message from client",message)
        content = json.loads(message['content'])

        # look up key and route message
        if content["key"] == "prime_player_command":
            await self.prime_player_command(content)
        pass

    @staticmethod
    async def __block_until_false(some_boolian, freq=0.5):
        """
        This method blocks flow and checks every freq second,
        if boolian is false, it returns nothing
        :param some_boolian:
        :param freq:
        :return:
        """
        while some_boolian:
            await asyncio.sleep(freq)
        return


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
        controllers.silly_print("message received by Game Processor",event)

        match_id = event['match_id']
        prime_channel_name = event['prime_channel_name']
        game_controller = controllers.GameController(match_id=match_id)

        game_controller.initialize_state()
        query_set = game_controller.get_query_set(game_controller.current_state)

        message = {
            "type": "process_query_set",
            "match_id": match_id,
            "query_set": query_set
        }

        async_to_sync(self.channel_layer.send)(prime_channel_name, message)
        controllers.silly_print("message sent by Game Processor",message)

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

        query_set = game_controller.get_query_set(game_controller.current_state)

        message = {
            "type":"process_query_set",
            "match_id": match_id,
            "query_set":query_set
        }

        async_to_sync(self.channel_layer.send)(prime_channel_name, message)
        controllers.silly_print("message sent by Game Processor",message)

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

        game_controller.apply_query_response(game_controller.current_state,response_set)

        # send update message to all in game group
        content = game_controller.dump_state_to_json(game_controller.current_state)
        update = {
            "type":"world.update",
            "content":content
        }
        async_to_sync(self.channel_layer.send)(match_id,update)
        controllers.silly_print("message sent by Game Processor",update)

        # send message to prime to signal process complete
        message = {
            "type":"process.response.complete",
            "match_id": match_id
        }
        async_to_sync(self.channel_layer.send)(prime_channel_name, message)
        controllers.silly_print("message sent by Game Processor", message)


class BotProcessorConsumer(SyncConsumer):
    """
    This consumer handles decision request from player prime.
    This object is stateless, all game state data comes from db lookup

    methods callable by channels:

    - respond_query

    """
    def respond_query(self,event):
        """

        :param event:
        :return:
        """
        # debug print
        controllers.silly_print("message received by Bot Processor",event)

        # var look up
        query_set = event['query_set']
        player_num = event['player_num']
        match_id = event['match_id']
        prime_channel_name = event['prime_channel_name']

        # init tree search controller
        lorax = controllers.SearchController(query_set,player_num,match_id)

        # if we want the bot to access past data unhex the line below
        lorax.load_simulation_data()

        # run sim and respond to q set
        response_set = lorax.respond_to_query_set()

        # send response message to prime player
        message = {
            "type":"process.client.response",
            "response_set":response_set
        }

        async_to_sync(self.channel_layer.send)(prime_channel_name, message)
        controllers.silly_print("message sent by Bot Processor",message)

