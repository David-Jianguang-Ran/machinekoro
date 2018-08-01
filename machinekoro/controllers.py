import json
import math
import random
import time
import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from . import models
from . import game_state


class MatchController:
    """
    This object has methods needed to manage data needed for PlayerConsumer

    O instance variables:
    - token_namespace = uuid namespace used to generate token
    - match_namespace = uuid namespace used to generate match_id

    O methods callable by views:

    - initialize_new_match

    - add_player_to_match

    O methods callable by consumers:

    # fancy feature, ignore for now
    - update_player_name

    - look_up_by_token

    - switch_prime_player

    O private methods:

    - __register_to_token_table

    """
    def __init__(self):
        self.token_namespace = uuid.UUID('e1051943-f6d0-47b0-944d-2f7004d92804')
        self.match_namespace = uuid.UUID('ea29425f-ebb4-45aa-ae46-18e28b0dd650')

    def initialize_new_match(self):
        """
        this method creates a new match session and assign it with a match_uuid
        all other fields are left blank until a match starts
        :return: match_id string
        """
        # make a uuid string based on time stamp and rand num
        timestamp_plus_some = str(int(time.time())) + str(random.random())
        match_id_str = str(uuid.uuid5(self.match_namespace, timestamp_plus_some))
        register_json = json.dumps({})  # is dumping nothing necessary?

        # create MatchSession model
        match_obj = models.MatchSession.objects.create(match_id=match_id_str,register=register_json)
        match_obj.save()
        return match_id_str

    def add_player_to_match(self, match_id, prime=False, bot=False):
        """
        -note- first player in any game should always be prime
        this sync method could be called by both views and consumers!
        this method looks up existing match register and
        SENDS a new game register to all in group by match_id via channel_layer
        ADDS entry to both matchSession and token register
        :param match_id: uuid string
        :param prime: bool
        :param bot: bool
        :return: token uuid string -or- None if bot is added
        """
        # looks up db object by match_id and load json content
        match_obj = models.MatchSession.objects.get(match_id=match_id)
        match_register = json.loads(match_obj.register)

        # create new register entry
        num = len(match_register) + 1
        register_entry = {
            'match_id': match_id,
            'player_num': num,
            'is_prime': prime,
            'is_bot': bot,
            # should i add a customizable name & portrait here?
        }
        match_register['num'] = register_entry

        # saves match register to db
        match_obj.register = json.dumps(match_register)
        match_obj.save()

        # if this is not the first player(prime player) in a game,
        # send a message in channel_layer to all in group to update new player info
        if not prime:
            message = {
                "type": "prime.register.update",
                "content": match_register  # do i need to serialize this ? I hope not
            }
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(match_id, message)

        # if new player is a human player, add register to TokenRegister model
        if not bot:
            token = self.__register_to_token_table(register_entry, match_id)
            return token

    def __register_to_token_table(self, content, match_id):
        """
        this method takes some content(consumer init data obj) and a match_id
        does proper storage in db, and return a uuid string(i know it's not a real uuid)
        :param content: consumer setting dict obj
        :param match_id: string MatchSession uuid
        :return: token( uuid string )
        """
        content_json = json.dumps(content)
        token_str = str(uuid.uuid5(self.token_namespace,content_json))

        # create register obj
        register_obj = models.TokenRegister.objects.create(
            token=token_str,
            content=content_json
        )
        register_obj.save()

        # add register to  match obj, registers field
        match_obj = models.MatchSession.objects.get(match_id=match_id)
        match_obj.registers_set.add(register_obj)
        match_obj.save()
        return token_str

    @staticmethod
    def initialize_by_token(token_str,channel_name):
        """
        This method looks up setting dict by token, does modification based on consumer name then return it
        :param token_str: string uuid
        :param channel_name: channel name of the consumer being initialized
        :return: dict consumer settings
        """
        # gets register db object and loads content
        register_obj = models.TokenRegister.objects.get(token=token_str)
        content = json.loads(register_obj.content)

        content['self_channel_name'] = channel_name

        # save new content to db
        content_json = json.dumps(content)
        register_obj.content = content_json
        register_obj.save()
        return content

    @staticmethod
    def switch_prime_player():
        # not very sure about this
        pass


class GameController:
    """
    this object is used to manage loading/saving and running the game

    O methods callable by State processor:

    - initialize_state

    - get_query_set

    - process_query_response

    """
    def __init__(self, match_id=None):
        self.current_state = None
        self.match_id = None
        if match_id:
            self.__load_state_from_db(match_id)
            self.match_id = match_id

    def initialize_state(self):
        """

        :return: None
        """
        self.current_state = "some state obj"
        pass

    def get_query_set(self):
        """
        you must have a state loaded in self.current_state before calling this method
        :return: sends query set to be distributed by player prime's consumer
        """
        query_set = self.current_state.get_legal_moves()
        return query_set

    def process_query_response(self,response_set):
        """
        this methods takes a response set and apply all decisions from them then advance state
        then broadcast new state to group
        :param response_set: response objs sent from player prime
        :return:
        """

        self.__save_state_to_db()
        pass

    def __send_game_state_update(self):
        # dump current state into json_set
        json_set = self.__dump_state_to_json(self.current_state)

        message = {
            "type": "game.state.update",
            "match_id":self.match_id ,
            "content": json_set  # do i need to serialize this ? I hope not
        }
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(self.match_id, message)

    def __load_state_from_db(self, match_id):
        """
        this method loads db obj by game id,
        :param match_id:
        :return: nothing, modifys self.current_state
        """
        matchsession = models.MatchSession.objects.get(match_id=match_id)
        tracker = json.loads(matchsession.tracker)
        market = json.loads(matchsession.market)
        players = json.loads(matchsession.player_list)
        self.current_state = game_state.GameState(players,market,tracker)

    def __save_state_to_db(self):
        """
        this method takes a state and write data to corresponding MatchSession model
        :return: Nothing, it just modifis db
        """
        # prepare json from world state
        json_set = self.__dump_state_to_json(self.current_state)

        # save data to db
        match = models.MatchSession.objects.filter(match_id=self.match_id)
        match.update(
            tracker=json_set['tracker'],
            market=json_set['market'],
            player_list=json_set['players']
        )
        match.save()

    @staticmethod
    def __dump_state_to_json(state):
        # prepare json from state
        tracker_json = json.dumps({
            "hand_count": state.hand_count,
            "active_player": state.hand_count % len(state.players),
            "phase": state.phase
        })
        market_json = json.dumps(state.market)
        player_list_json = json.dumps(state.players)

        json_set = {
            'tracker' : tracker_json,
            'market' : market_json,
            'players' : player_list_json
        }
        return json_set


class SearchController:
    """
    this object is used to load a state, perform simulation and make decision
    """
    def __init__(self):
        pass

    def run_sim(self):
        """
        This method runs MCTS using UCB1. modifies the stats attributes self.plays , wins , states

        :return:
        """