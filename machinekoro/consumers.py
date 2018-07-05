from channels.generic.websocket import SyncConsumer,AsyncConsumer,AsyncWebsocketConsumer
from asgiref.sync import async_to_sync,sync_to_async
import json
import time
import copy
from . import models

# note: there is no routing connected to the consumers yet
# also:
#   how do i instanciate the dealersocket without duplacation?
#   should bot socket be 'dedicated' to each botplayer? or should to be shared by all the bots? should it persist?



class PlayerSocket(AsyncWebsocketConsumer):
    # this is a Player ws consumer object,
    # the channel_layer group attribute reflect the game "room" the player is in
    # methods connect, disconnect and recieve has been defined
    async def connect(self):
        # connect to the room specified in url
        self.game_serial = self.scope['url_route']['kwargs']['serial']
        self.session = self.scope['session']
        await self.channel_layer.group_add(
            self.game_serial,self.channel_name
        )
        await self.channel_layer.group_send({
            "type":"initialize.player" ,
            "session_name": self.session ,
            "channel_name":self.channel_name
        })

    async def receive(self, text_data=None, **kwargs):
        # this method is called when a ws msg from client is recieved
        #  action_query , world_update
        data_obj = json.loads(text_data)
        mode = data_obj['subtype']
        if mode == 'msg_to_dealer':
            data_obj['type'] = ""
            await self.channel_layer.send(
                self.dealer_channel_name,data_obj)
        elif mode == 'admin_cmd' and self.prime :
            await self.channel_layer.send(
                self.dealer_channel_name,data_obj)
        else:
            await self.send({
                "mode":'error',
                'error_msg':'unknown subtype'
            })

    async def msg_to_client(self, event):
        text = json.dumps(event)
        self.send(text_data=text)

    async def disconnect(self, code):
        # disconnects from room
        await self.channel_layer.group_discard(
            self.game_serial,self.channel_name
        )

    async def client_initialization(self,event):
        # this method is called by a msg from dealersocket
        # player_num, dealer channel name are captured from massage and saved as instance var
        self.player_num = event['player_num']
        self.dealer_channel_name = event['dealer_channel_name']
        if event['prime_player']:
            self.prime = True
        pass


class BotSocket(SyncConsumer):
    # this consumer does not send any messages over WS
    # BotSocket reads message in "room" and drives the ai with it
    def initialize_bot(self):
        self.lorax = models.TreeSearchController()
    pass


class DealerSocket(AsyncConsumer):
    # i do wonder if processing post dice_roll user inputs would benefit from being async
    async def http_request(self,event):
        # can i just call views from views.py from here?
        pass

    async def http_disconnect(self,event):
        pass

    async def run_game(self):
        # this method is called by prime player to start the main game loop
        winner = False
        while not winner:
            # this method determines active player, gets all legal moves and prepares query to user
            # the outgoing queries are tracked
            # then it sends the query(s) to the corresponding players
            # once all responses are in, it calls SYNC advance_state function to apply actions
            # then it saves state to to db

            # gets a lets of query objects
            query_list = await sync_to_async(self.game_obj.current_state.get_legal_moves())
            # if the query has no recipient, it signals the message has only one possible option
            # it will be sent directly to response list
            # queries with recipient will be sent via channel_layer
            response_list = []
            for query in query_list:
                if not query['channel_name']:
                    response = copy.deepcopy(query)
                    response['choice'] = response['options']
                else:
                    self.channel_layer.send(query['channel_name'],query)

    async def initialize_player(self,event):
        # this method takes the handshake message, saves data to state then sends lobby update to all in channel
        register_entry = {
            "session": event['session_name'] ,
            "channel_name": event['channel_name']
        }
        new_player = True
        num = None
        for key , value in self.register.items():
            if value['session'] == register_entry['session']:
                new_player = False
                num = key
        if new_player:
            player = sync_to_async(self.syc_initialize_player(register_entry['channel_name']))
            register_entry['player_num'] = player.num
            response = {
                "type": "client.initialization",
                "player_num": player.num,
                "dealer_channel_name": self.channel_name
            }
            self.register[player.num] = register_entry
        else:
            self.register[num]['channel_name'] = register_entry["channel_name"]
            response = {
                "type": "client.initialization",
                "player_num": num,
                "dealer_channel_name": self.channel_name
            }
        await self.channel_layer.send(
            register_entry['channel_name'],response)
        await self.channel_layer.group_send()

    async def update_main(self):
        # this method broadcasts the current world state into the room
        state_json = await json.dumps(self.game_obj.current_state)
        await self.channel_layer.group_send(
            self.game_obj.serial, {
                'type': 'msg.to.client',
                'subtype':'world_update',
                'content': state_json
            })

    async def update_lobby(self):
        # this method braodcasts everything needed for lobby
        data = await self.game_obj.get_lobby_display()
        state_json = await json.dumps(data)
        await self.channel_layer.group_send(
                self.game_obj.serial,
            {
                'type': 'msg_to_client',
                'subtype':'lobby_update',
                'content': state_json ,
                "dealer_channel_name" :self.channel_name
        })

    def syc_initialize_session(self):
        # initialize game controller
        serial = int(time.time())
        self.game_obj = models.GameController(serial)
        # create in memory object to store client info
        self.register = {}
        # initialize channel group and connect
        self.channel_layer.group_add(
            self.serial,self.channel_name
        )

    def syc_initialize_player(self,channel_name):
        # querys db for player count
        q_set = models.Player.objects.filter(game = self.game_obj)
        if q_set:
            player_num = len(q_set)
        else:
            player_num = 0
        name = "Player"+ channel_name
        player = models.Player(player_num,name=name)
        self.game_obj.save_player_to_db(player)
        return player


