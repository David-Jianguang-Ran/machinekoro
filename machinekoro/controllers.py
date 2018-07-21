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
    this object is used to manage loading/unloading and running the game

    """
    def __init__(self):
        pass


class SearchController:
    """
    this object is used to load a state, perform simulation and make decision
    """
    def __init__(self):
        pass
