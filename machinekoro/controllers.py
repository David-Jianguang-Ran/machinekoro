import json
import math
import random
import time
import uuid

from . import models
from . import game_state


class MatchController:
    """
    This object has methods needed to manage data needed for PlayerConsumer

    O class variables:
    - token_namespace = uuid namespace used to generate token
    - match_namespace = uuid namespace used to generate match_id

    O methods callable by views:

    - initialize_new_match

    - add_player_to_match

    O methods callable by consumers:

    - look_up_by_token

    - switch_prime_player

    O private methods:

    - __register_to_token_table

    """
    token_namespace = uuid.UUID('e1051943-f6d0-47b0-944d-2f7004d92804')
    match_namespace = uuid.UUID('ea29425f-ebb4-45aa-ae46-18e28b0dd650')

    def initialize_new_match(self):
        """
        this method creates a new match session and assign it with a match_uuid
        all other fields are left blank until a match starts
        :return: match_id string
        """
        # make a uuid string based on time stamp and rand num
        timestamp_plus_some = str(int(time.time())) + str(random.random())
        match_id_str = str(uuid.uuid5(self.match_namespace,timestamp_plus_some))
        register_json = json.dumps({})

        # create MatchSession model
        match_obj = models.MatchSession.objects.create(match_id=match_id_str,register=register_json)
        match_obj.save()
        return match_id_str

    def add_player_to_match(self, match_id, prime=False):
        """
        this method looks up existing match register and
        ADDS entry to both matchSession and token register
        :param match_id: uuid string
        :param prime: bool
        :return: token uuid string
        """
        match_obj = models.MatchSession.objects.get(match_id=match_id)
        match_register = json.loads(match_obj.register)

        num = len(match_register) + 1
        register_entry = {
            'match_id': match_id,
            'player_num': num,
            'is_prime': prime,
            'is_bot': False,
        }

        match_register['num'] = register_entry
        match_obj.register = json.dumps(match_register)
        match_obj.save()

        token = self.__register_to_token_table(register_entry, match_id)
        return token

    def __register_to_token_table(self, content, match_id):
        """
        this method takes some content(consumer init data obj) and a match_id
        does proper storage in db, and return a uuid string(i know it's not a real uuid)
        :param content: consumer setting dict obj
        :param match_id: string MatchSession uuid
        :return: token( uuid string)
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
    def initialize_by_token(token_str):
        """
        This method looks up setting dict by token, then return it
        :param token_str: string uuid
        :return: dict consumer settings
        """
        register_obj = models.TokenRegister.objects.get(token=token_str)
        content = json.loads(register_obj.content)
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

    def initialize_state(self,player_count):
        """

        :param player_count:
        :return: None
        """
        self.current_state = "some state obj"
        self.match_id = "some match id"
        pass

    def get_query_set(self):
        """
        you must have a state loaded in self.current_state before calling this method
        :return: query set to be distributed by player prime's consumer
        """
        query_set = []
        return query_set

    def process_query_response(self,response_set):
        """
        this methods takes a response set and apply all decisions from them then advance state
        :param response_set: response objs sent from player prime
        :return:
        """

        self.__save_state_to_db(self.current_state,self.match_id)
        pass

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

    @staticmethod
    def __save_state_to_db(state, match_id):
        """
        this method takes a state and write data to corresponding MatchSession model
        :param state:
        :param match_id: session uuid string
        :return: Nothing, it just modifis db
        """
        # prepare json from state
        tracker_json = json.dumps({
            "hand_count": state.hand_count,
            "active_player": state.hand_count % len(state.players),
            "phase": state.phase
        })
        market_json = json.dumps(state.market)
        player_list_json = json.dumps(state.players)

        # save data to db
        match = models.MatchSession.objects.filter(match_id=match_id)
        match.update(
            tracker=tracker_json,
            market=market_json,
            player_list=player_list_json
        )
        match.save()


class SearchController:
    """
    this object is used to load a state, perform simulation and make decision
    """
    def __init__(self):
        pass
