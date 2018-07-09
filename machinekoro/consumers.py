from channels.generic.websocket import SyncConsumer,AsyncConsumer,AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync,sync_to_async
import asyncio
import json
import time
import copy
from . import models

# note: there is no routing connected to the consumers yet
# also:
#   how do i instanciate the dealersocket without duplacation?
#   should bot socket be 'dedicated' to each botplayer? or should to be shared by all the bots? should it persist?


class PlayerSocket(AsyncJsonWebsocketConsumer):
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

    async def msg_to_client(self, event):
        # passes message onto client over ws
        await self.send_json(event)

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
        client_msg = {
            "c_type":"client.init",
            "player_num":self.player_num
        }
        await self.send_json(client_msg)

    async def initialize_player(self):
        # dummy event handler put here to prevent potential errors
        # remove during optimization
        pass

    async def receive_json(self, content, **kwargs):
        # this method is called when a ws msg from client is recieved
        #
        mode = content['c_type']
        if mode == 'query_response':
            content['type'] = "query.response"
            await self.channel_layer.send(
                self.dealer_channel_name,content)
        elif mode == 'admin_cmd' and self.prime:
            await self.channel_layer.send(
                    self.dealer_channel_name,content)
        else:
            await self.send_json({
                "mode":'error',
                'error_msg':'unknown subtype'
            })


class BotSocket(SyncConsumer):
    # this consumer does not send any messages over WS
    # BotSocket reads message in "room" and drives the ai with it
    # bots are initialized via http requests sent from prime player in lobby
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
            # [on hold]then it saves state to to db <= we'll see about this later i'll have to decide:
            # the data storage needs, lt vs st, and whether to record state or decision stream

            # gets a lets of query objects
            query_list = sync_to_async(self.game_obj.current_state.get_legal_moves())
            # can you just await arbitrary sync functions instead?

            # if the query has no recipient, it signals the message has only one possible option
            # it will be sent directly to response list
            # queries with recipient will be sent via channel_layer
            for query in query_list:
                if not query['channel_name']:
                    response = copy.deepcopy(query)
                    response['choice'] = response['options']
                    self.response_list.append(query)
                else:
                    self.channel_layer.send(query['channel_name'],query)

            # the blocking function blocks process until all response are received
            query_response_all = await self.block_untill_response(query_list)

            # call advance_state function to apply changes
            sync_to_async(self.game_obj.current_state.advance_state(query_response_all))

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
            # !!! what's with the attribution error here?
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
        await self.update_main()

    async def update_main(self):
        # this method broadcasts the current world state into the room
        # prepare_json object
        state_json = await json.dumps(self.game_obj.current_state)
        await self.channel_layer.group_send(
            self.game_obj.serial, {
                'type': 'msg.to.client',
                'c_type':'world_update',
                'content': state_json
            })

    async def update_lobby(self):
        # this method broadcasts everything needed for lobby
        data = await self.game_obj.get_lobby_display()
        lobby_json = await json.dumps(data)
        await self.channel_layer.group_send(
                self.game_obj.serial,
            {
                'type': 'msg.to.client',
                'c_type':'lobby_update',
                'content': lobby_json ,
                "dealer_channel_name" :self.channel_name
        })

    async def block_untill_response(self,query_list):
        # this co-routine checks if all the responses are in,
        # if so, it returns the response list and clears the self.response_list
        # prepares a list of snapshot of query to match against
        snapshot_q = []
        for query in query_list:
            entry = [query['player_num'],query['q_type']]
            snapshot_q.append(copy.copy(entry))

        # check every 100ms if all response are in (i hope 100ms isn't too frequent)
        while snapshot_q != self.snapshot_r:
            await asyncio.sleep(0.1)
        # if so, return response list (the attributes are cleaned after advance state)
        return self.response_list

    async def query_response(self,event):
        # this event handler takes message send over the channel_layer with 'type' query response
        # result of the message along with snapshot_r is save as attributes

        # prepare snapshot
        snap = [event['player_num'],event['q_type']]

        # append msg and snap to memory
        await self.response_list.append(event)
        await self.snapshot_r.append(snap)

    # the sync functions below SHOULD NOT be called directly by the consumer without sync_to_async
    def syc_initialize_session(self):
        # initialize game controller
        serial = int(time.time())
        self.game_obj = models.GameController(serial)
        # create in memory object to store client info
        self.register = {}
        # create in memory object for query responses
        self.response_list = []
        self.snapshot_r = []
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

