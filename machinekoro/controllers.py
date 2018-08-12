import copy
import collections
import json
import math
import random
import time
import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from . import models
from . import game_objects

# debug print var, remember to set to false NoteK@88
DEBUG_PRINT = True


def silly_print(str,content):
    if DEBUG_PRINT:
        print(str)
        print(content)


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
        match_obj = models.MatchSession.objects.create(match_id=match_id_str,register=register_json,in_progress=False)
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

        # bail out early if no match_obj with the id
        if not match_obj:
            return

        match_register = json.loads(match_obj.register)

        if match_obj.in_progress:
            return
        else:
            # create new register entry
            num = int(len(match_register) + 1)
            register_entry = {
                'match_id': match_id,
                'player_num': num,
                'is_prime': prime,
                'is_bot': bot,
                # should i add a customizable name & portrait here?
        }
        match_register[num] = register_entry

        # saves match register to db
        match_obj.register = json.dumps(match_register)
        match_obj.save()

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

        # look up match obj
        match_obj = models.MatchSession.objects.get(match_id=match_id)

        # create register obj
        register_obj = models.TokenRegister.objects.create(
            token=token_str,
            content=content_json,
            match_session=match_obj
        )
        register_obj.save()
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

        # register look up and modification
        match_id = content['match_id']
        player_num = content['player_num']
        content['self_channel_name'] = channel_name

        # gets MatchSession object
        match_obj = models.MatchSession.objects.get(match_id=match_id)
        prime_register = json.loads(match_obj.register)

        # remove old entry from add player step then add new register entry that includes self.channel_name
        prime_register.pop(str(player_num), None)
        prime_register[int(player_num)] = content

        silly_print("prime_register at init by token",prime_register)

        # if this is not the first player(prime player) in a game,
        # send a message in channel_layer to all in group to update new player info
        if not content['is_prime']:
            message = {
                "type": "prime.register.update",
                "content": prime_register  # do i need to serialize this ? I hope not
            }
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(match_id, message)

        # save new content to db
        register_obj.content = json.dumps(content)
        register_obj.save()

        match_obj.register = json.dumps(prime_register)
        match_obj.save()
        return content

    @staticmethod
    def handle_player_disconnect(discon_register):
        """
        This method takes a player register, change is_bot to true, if player is prime, another prime is selected
        then everything is saved to db
        note the the token register will not be updated,
        but since no player can have the same num, the token will not be needed anymore
        :param register:
        :return:
        """
        # save some variables in memory
        match_id = discon_register['match_id']
        discon_num = discon_register['player_num']
        # look up and load prime register by match_id
        match_obj = models.MatchSession.objects.get(match_id=match_id)
        prime_register = json.loads(match_obj.register)
        # set disconnected player to bot
        discon_register['is_bot'] = True
        if discon_register['is_prime']:
            # choose one from a list of num of human players
            human_players = [key for key in prime_register if not prime_register[key]['is_bot']]
            new_prime = random.choice(human_players)
            # set this player to prime
            prime_register[new_prime]['is_prime'] = True
            # set discon to not prime
            discon_register['is_prime'] = False

        # save new discon register to prime, then to db
        prime_register[discon_num] = discon_register
        prime_register_json = json.dumps(prime_register)
        match_obj.register = prime_register_json
        match_obj.save()

        # send update to group
        message = {
            "type": "prime.register.update",
            "content": prime_register_json
        }
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(match_id, message)


class GameController:
    """
    this object is used to manage loading/saving and running the game
    this object is child for game processor consumer or tree search controller
    O methods:

    - initialize_state

    - get_query_set

    - apply_query_response

    """
    def __init__(self,match_id):
        self.match_id = match_id

        match_session = models.MatchSession.objects.get(match_id=match_id)

        if match_session.in_progress:
            self.__load_state_from_db(match_session)
        else:
            self.current_state = None

    def initialize_state(self):
        """
        This method is called by the prime player with type "initialize.state"
        This method sets up a state to hold in self.current state and saves it to db also
        :return:
        """
        match_session = models.MatchSession.objects.get(match_id=self.match_id)
        prime_register = json.loads(match_session.register)

        self.current_state = game_objects.GameState(len(prime_register))

        self.__save_state_to_db()

    @staticmethod
    def get_query_set(state):
        """
        # the possible values for phase:
        # pre_roll > post_roll > pre_activation > post_activation > post_card_play > Pre_roll

        :param state:
        :return:
        """
        phase = state.tracker['phase']
        active_player_num = state.tracker['active_player_num']
        active_player = state.players[active_player_num]

        # bool flag for taking double turn
        take_duce = False

        # pre_roll phase
        #
        if phase == 'pre_roll':
            # returns a query object with allowed dice options
            query = {
                "key" : "action.query",
                "player_num" : active_player_num,
                "q_type":"dice_query_a"
            }
            if active_player['landmark']['Train Station'] == 1:
                if active_player['landmark']['Moon Tower'] == 1:
                    query['options'] = [1,2,3]
                else:
                    query['options'] = [1,2]
            else:
                query['options'] = [1]
                query['only_option'] = True
            return [query]

        # post_roll Phase
        elif phase == 'post_roll':
            # returns the  list of queries to active player to choose which diceroll to apply
            dice_roll = state.temp_data['dice_roll']

            query = {
                "key": "action.query",
                "player_num": active_player_num,
                "q_type": "dice_query_b",
                "options": dice_roll
            }
            if len(dice_roll) != 3:
                query['only_option'] = True
            return [query]

        #
        elif phase == "pre_activation":
            activation = state.temp_data['activation']

            # returns a query asking whether to apply harbour (activation + 2)
            if active_player['landmark']['Harbor'] == 1 and activation >= 10:
                query = {
                    "key": "action.query",
                    "player_num": active_player_num,
                    "q_type": "dice_query_c",
                    "options": [True,False]
                }
            else:
                query = {
                    "key": "action.query",
                    "player_num": active_player_num,
                    "q_type": "dice_query_c",
                    "options": [True, False],
                    "only_option" : True
                }
            return [query]

        #
        elif phase == 'activation':
            query_set = state.temp_data['query_set']
            # ??? what the hell is this? what does this do?
            # answer: no query is prepared here because query from card activation must be generated
            # when the card action is applied, therefore here we only copy queries from an attribute and return them
            return query_set

        #
        elif phase == "post_activation":
            # returns a query object with allowed card play
            coin = active_player.coin
            market = state.market
            options = []
            for some_card in market.high:
                if coin >= market.deck_info[some_card].cost:
                    options.append(some_card)
            for some_card in state.market.low:
                if coin >= market.deck_info[some_card].cost:
                    options.append(some_card)
            for some_card in state.market.purple:
                if coin >= market.deck_info[some_card].cost and some_card not in active_player.hand:
                    options.append(some_card)

            # if player has airpot, add another option
            if active_player['landmark']['Airport']:
                options.append('Activate Airport')

            query_list = [{
                "key" : "action.query" ,
                "player_num" : active_player_num,
                "q_type": "card_play_query",
                "options": options
            }]
            return query_list

        #
        elif phase == "post_card_play":
            # returns query object with tech start-up or whatever
            query_list = []
            if 'Tech Start-up' in active_player.hand and active_player.coin > 0 :
                query = {
                    "key" : "action.query" ,
                    "player_num" : active_player_num,
                    "q_type": "invest_query",
                    "options": [True,False]
                }
                query_list.append(query)

            if state.temp_data['duces']:
                query = {
                    "key" : "action.query" ,
                    "player_num" : active_player_num,
                    "q_type": "duces_query",
                    "options": [True,False]
                }
                query_list.append(query)
                # Clean up
                state.temp_data['duces'] = False

            return query_list

    def apply_query_response(self,state,response_set):
        """

        :param state:
        :param response_set:
        :return:
        """
        phase = state.tracker['phase']
        active_player_num = state.tracker['active_player_num']
        active_player = state.players[active_player_num]
        take_duce = False

        if phase == 'pre_roll':
            for response in response_set:
                # rolls dice according to choice
                if response['player_num'] == active_player_num and response['q_type'] == 'dice_query_a':
                    # check if message is the right type and num
                    diceroll = []
                    i = response['choices']
                    n = 0
                    while n < i :
                        diceroll.append(random.choice(range(1,7)))
                        n += 1
                    state.temp_data['dice_roll'] = diceroll
                else:
                    print("Miss matched query during pre_roll process")
            state.tracker['phase'] = 'post_roll'

        elif phase == 'post_roll':
            # takes a list of query responses and applies all to the state empty snippet
            for response in response_set:
                if response['player_num'] == active_player_num and response['q_type'] == 'dice_query_b':
                    state.temp_data['dice_roll'] = response['choices']

                    # check for doubles
                    if response['choices'][0] == response['choices'][1]:
                        state.temp_data['duces'] = True
                    state.temp_data['activation'] = sum(state.temp_data['dice_roll'])
                else:
                    print("Miss matched query during post_roll process")
            state.tracker['phase'] = 'pre_activation'

        elif phase == "pre_activation":
            # takes the query and modify activation and and calculates activation
            choice = None
            activation = state.temp_data['activation']
            for response in response_set:
                if response['player_num'] == active_player_num and response['q_type'] == 'dice_query_c':
                    choice = response['choices']
                    if choice is False:
                        pass
                    elif choice is True:
                        activation += 2
                    pass
                else:
                    print("Miss matched query during pre_activation process")

            # sends an update for activations
            message = {
                'type':"dice.roll.update",
                "dice_roll":state.temp_data['dice_roll'],
                "harbour_+2": choice
            }
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(self.match_id, message)

            # applies activation to all player's hand, collect query and add to state.temp_data with key query_set
            self.__resolve_activation(state,activation)

            # increment phase tracker
            state.tracker.phase = 'activations'

        elif phase == "activation":
            # takes state and query generated from activations and modifies and returns the state
            if response_set:
                for response in response_set:
                    if response['q_type'] == 'card_query_demo':
                        choice = response['choices']
                        active_player['landmark'][choice] = 0
                        active_player.coin += 8
                    elif response['q_type'] == 'card_query_move':
                        card_choice = response['choices'][0]
                        player_choice = state.players[response['choices'][1]]
                        for card in active_player.hand and card == card_choice:
                            player_choice.hand.append(card)
                            active_player.hand.remove(card)
                            active_player.coin += 4
                    elif response['q_type'] == "card_query_trade":
                        self_choice = response['choices'][0]
                        target_player = state.players[response['choices'][1].key()]
                        target_card = response['choices'][1].value()
                        for card in active_player.hand and card == self_choice:
                            target_player.hand.append(card)
                            active_player.hand.remove(card)
                        for card in target_player.hand and card == target_card:
                            active_player.hand.append(card)
                            target_player.hand.remove(card)
            elif not response_set:
                print("No response received advance state without action")

            # landmark['City Hall'] logic:
            if active_player.coin == 0:
                active_player.coin = 1

            state.tracker['phase'] = 'post_activation'

        elif phase == "post_activation":
            # takes state and play card action and modifies and returns the state
            # card play happens here
            # remember to charge for cards!!!
            for response in response_set:
                if response['player_num'] == active_player_num and response['q_type'] == 'card_play_query':
                    card_choice = response['choices']
                    # landmark['Airport'] logic here
                    if card_choice == "Activate Airport":
                        active_player.coin += 10
                    elif card_choice in ["City Hall","Harbour","Train Station",
                                         "Shopping Mall","Amusement Park",
                                         "Moon Tower","Airport"]:
                        active_player['landmark'][card_choice] = 1
                    else:
                        self.__buy_card_from_market(state,active_player,card_choice)

            # if winner, write winner num to state
            state.tracker['winner'] = self.__check_winner(state)
            state.tracker['phase'] = 'post_card_play'

        elif phase == "post_card_play":
            if response_set:
                for response in response_set:
                    if response['player_num'] == active_player_num and response['q_type'] == 'invest_query':
                        # choice to invest 1 coin or not
                        if response['choices']:
                            active_player.investment += 1
                            active_player.coin -= 1
                        else:
                            pass
                    elif response['player_num'] == active_player_num and response['q_type'] == 'duces_query':
                        # choice to take a another turn or not
                        if response['choices']:
                            take_duce = True

            state.tracker.phase = 'pre_roll'

            if state.temp_data['duces'] and take_duce:
                state.temp_data['duces'] = False
            else:
                state.tracker['active_player_num'] += 1
                if state.tracker['active_player_num'] > len(state.players):
                    state.tracker['active_player_num'] = 1

        return state

    @staticmethod
    def __resolve_activation(state,activation_num):
        active_player_num = state.tracker['active_player_num']
        active_player = state.players[active_player_num]

        query_set = []

        for some_player in state.players:
            # activate active player hand (non-red)
            if some_player.num == active_player_num:
                for some_card_name in some_player.hand:
                    card_info = game_objects.CardDex[some_card_name]
                    if card_info['activation'] == activation_num and card_info['colour'] in ['Blue','Green','Purple']:
                        card_obj = game_objects.Card(some_card_name)
                        # some activation may generate query to player
                        any_query = card_obj.activate(state,active_player)
                        query_set.append(any_query)
            # activate other player blue and red
            else:
                for some_card_name in some_player.hand:
                    card_info = game_objects.CardDex[some_card_name]
                    if card_info['activation'] == activation_num and card_info['colour'] in ['Blue','Red']:
                        card_obj = game_objects.Card(some_card_name)
                        # some activation may generate query to player
                        any_query = card_obj.activate(state,active_player,some_player)
                        query_set.append(any_query)

        state.temp_data['query_set'] = query_set

    @staticmethod
    def __buy_card_from_market(state,active_player,card_choice):
        """
        This method modifies the market according to what card the player has decided to purchase
        This methos also replenishes the piles and modifies deck_info accordingly
        :param state:
        :param active_player:
        :param card_choice:
        :return:
        """
        market = state.market
        card_info = market.deck_info[card_choice]

        if card_info['cost'] >= active_player.coin:
            if card_info['type'] == 'low':
                market.low[card_choice] -= 1
            elif card_info['type'] == 'high':
                market.high[card_choice] -= 1
            elif card_info['type'] == 'purple' and card_choice not in active_player.hand:
                market.purple[card_choice] -= 1
        else:
            print(active_player + "unable to afford action:" + card_choice)

        list_o_pile_name = ['low','high','purple']

        for pile_type in list_o_pile_name:
            pile_dict = market[pile_type]
            # remove empty dict entires
            for key in pile_dict:
                if pile_dict[key] == 0:
                    pile_dict.pop(key)

            # keep drawing untill there are five type of cards for normal,
            # 2 types for purple
            if pile_type == 'purple':
                limit = 2
            else:
                limit = 5

            while len(pile_dict) < limit:
                    new_card_info = random.choice(market.deck_info)
                    if new_card_info['type'] == pile_type and new_card_info['limit'] > 0:
                        if pile_dict[new_card_info.name]:
                            pile_dict[new_card_info.name] += 1
                        else:
                            pile_dict[new_card_info.name] = 1

                        new_card_info['limit'] -= 1
                        break
                    else:
                        pass

    def __load_state_from_db(self, match_id):
        """
        this method loads db obj by game id,
        :param match_id:
        :return: nothing, modify self.current_state
        """
        matchsession = models.MatchSession.objects.get(match_id=match_id)
        json_data = {
            'tracker':matchsession.tracker,
            'market':matchsession.market,
            'players':matchsession.player_list,
            'temp_data':matchsession.temp_data
        }

        self.current_state = game_objects.GameState(json_set=json_data)

    def __save_state_to_db(self):
        """
        this method takes a state and write data to corresponding MatchSession model
        :return: Nothing, it just modify db
        """
        # prepare json from world state
        json_set = self.dump_state_to_json(self.current_state)
        silly_print("the following state has been saved to db ",json_set)

        # save data to db
        match = models.MatchSession.objects.get(match_id=self.match_id)

        match.in_progress = True
        match.tracker = json_set['tracker']
        match.market = json_set['market']
        match.player_list = json_set['players']
        match.temp_data = json_set['temp_data']

        match.save()

    @staticmethod
    def dump_state_to_json(state):
        # prepare json from state
        tracker_json = json.dumps(state.tracker)
        market_json = json.dumps(state.market)
        player_list_json = json.dumps(state.players)
        temp_data_json = json.dumps(state.temp_data)

        json_set = {
            'tracker': tracker_json,
            'market': market_json,
            'players': player_list_json,
            'temp_data': temp_data_json
        }
        return json_set

    @staticmethod
    def __check_winner(state):
        winner = None
        for some_player_num in state.players:
            if state.players[some_player_num]['landmark'] == {
                    "City Hall": True,
                    "Harbour": True,
                    "Train Station": True,
                    "Shopping Mall": True,
                    "Amusement Park": True,
                    "Moon Tower": True,
                    "Airport": True
            }:
                winner = some_player_num
        return winner


class SearchController:
    """
    this object is used to load a state, perform simulation and make decision

    O attributes:

    - query_set_prime = query set obj that needs to be responded list

    - game = game controller obj (also containing state)

    - stat_table = {  # used to keep simulation data
            'plays':{},
            'wins':{}
        }

    - max_moves = int

    - max_time = int (seconds)

    - max_depth_reached = int

    O methods:

    - run_sim

    - respond_to_query_set

    - save_simulation_data

    - load_simulation_data

    - get_move_states_from_query_set

    - choose_move_states_from_set

    """
    def __init__(self,query_set,num,match_id,max_moves= 20, max_time= 10, c=1.4):
        self.query_set_prime = query_set
        self.player_num = num
        self.game = GameController(match_id)
        self.c = c
        self.stat_table = {
            'plays':{},
            'wins':{}
        }
        self.max_moves = max_moves
        self.max_time = max_time
        self.max_depth_reached = 0

    def run_sim(self):
        """
        This method runs MCTS using UCB1. modifies the stats attributes self.plays , wins , states

        :return: nothing, this method updates self.stat_table as it runs
        """
        expansion_stage = True
        root = True
        # if i don't copy, will self.query_set_prime be modified?
        query_set = copy.copy(self.query_set_prime)

        sim_states = [copy.deepcopy(self.game.current_state)]
        current_state = sim_states[-1]
        current_player_num = current_state['tracker']['active_player'] # this is a int num, not a player obj
        visited_states = []

        stat_table = self.stat_table
        plays = stat_table['plays']
        wins = stat_table['wins']

        winner_found = None

        # with each iteration below, a move is made and a new state is visited and recorded
        for i in range(1,self.max_moves):
            # get query set or work with prime query set at root of tree
            if not root:
                query_set = self.game.get_query_set(current_state)
            else:
                root = False

            move_states = self.get_move_states_from_query_set(query_set,current_state)

            child_node_play_stats = [plays.get((current_player_num,state)) for move, state in move_states]
            if all(child_node_play_stats):
                # if there is stats for every node, use UCB1 to choose the next node
                log_total = math.log10(sum(child_node_play_stats))

                ucb_state_list = [ ( ( wins.get(current_player_num,state) / plays.get(current_player_num,state) ) +
                                    math.sqrt(2*log_total / plays.get(current_player_num,state) ) , state )
                                    for move, state in move_states]

                chosen_state = max(ucb_state_list)
            else:
                # if not randomly choose next node
                chosen_state = random.choice(move_states)[1]

            # if chosen_state is new to stat table move into expansion stage
            if not expansion_stage and (current_player_num,chosen_state) not in plays:
                expansion_stage = True
                plays[(current_player_num,chosen_state)] = 0
                wins[(current_player_num,chosen_state)] = 0
                # record max depth reached for fun
                if i > self.max_depth_reached:
                    self.max_depth_reached = i

            # record the state to lists
            sim_states.append(chosen_state)
            visited_states.append((current_player_num,chosen_state))

            # if a winner is found, break out of moving loop
            winner = chosen_state['tracker']['winner']
            if winner:
                winner_found = winner
                break

        # record data to self.stat_table
        for player, state in visited_states:
            if (player, state) not in plays:
                continue
            plays[(player,state)] += 1
            if player == winner_found:
                wins[(player,state)] += 1

    def respond_to_query_set(self):
        """
        This method takes a query_set, runs simulation based on it, and pick move_state and
        return response_set
        :return: response_set
        """
        # Run sim and record how many games have been played
        games = 0
        start_time = int(time.time())
        while int(time.time()) - start_time < self.max_time:
            self.run_sim()
            games += 1

        # get move states for prime query set
        move_states = self.get_move_states_from_query_set(self.query_set_prime,self.game.current_state)

        # pick move state with the highest percentage of wins
        most_win = 0
        selected_move = None
        for m, s in move_states:
            this_state = (self.player_num,s)
            win_ratio = self.stat_table['wins'].get(this_state) / self.stat_table['plays'].get(this_state)
            if win_ratio > most_win:
                selected_move = m

        # save sim data to improve search space mapping
        self.save_simulation_data()

        # return selected_move as it is a valid response set obj
        return selected_move

    def save_simulation_data(self,label="default"):
        """
        This method saves data generated by the run_sim step under a label string name
        :param label: there is only one label atm, 'default'
        :return:
        """
        # look up db vars
        db_obj = models.TreeSearchData.objects.get(label=label)
        plays_prime = json.loads(db_obj.plays)
        wins_prime = json.loads(db_obj.wins)

        # add new stats to db table
        plays_prime = collections.Counter(plays_prime) + collections.Counter(self.stat_table['plays'])
        wins_prime = collections.Counter(wins_prime) + collections.Counter(self.stat_table['wins'])

        # save to db
        db_obj.plays = json.dumps(plays_prime)
        db_obj.wins = json.dumps(wins_prime)
        db_obj.save()

    def load_simulation_data(self,label="default"):
        """
        This method loads data generated in previous sims and copy it to self.stat_table
        :param label: there is only one label atm, 'default'
        :return:
        """
        db_obj = models.TreeSearchData.objects.get(label=label)
        self.stat_table['plays'] = json.loads(db_obj.plays)
        self.stat_table['wins'] = json.loads(db_obj.wins)

    def get_move_states_from_query_set(self,query_set,state):
        """
        This method takes a query set, makes a move state for each possible combination of moves
        :param query_set:
        :param state: read only, not modified
        :return: move_states [(move,resulting_state),(...)]
        """
        moves = []
        first_q = True
        move_states = []

        # generate one move for each possible combination of responses(if multiple)
        # the moves are valid response_set object that could be used to advance state
        for some_query in query_set:
            move_set_calc = []
            if first_q:
                first_q = False
                for option in some_query['options']:
                    single_move = [{
                        "q_type": some_query['q_type'],
                        "player_num":some_query['player_num'],
                        "choice": option
                    }]
                    move_set_calc.append(single_move)
            else:
                for single_move in moves:
                    # add the child nodes of previous list elements
                    for option in some_query['option']:
                        new_entry = single_move.append({
                            "q_type":some_query['q_type'],
                            "player_num":some_query['player_num'],
                            "choice":option
                        })
                        move_set_calc.append(new_entry)
            # Saves new list as the list
            moves = move_set_calc

        # pair moves with the resulting state
        for move in moves:
            new_state = copy.deepcopy(state)
            new_state = self.game.apply_query_response(new_state,move)
            move_states.append((move,new_state))

        return move_states

