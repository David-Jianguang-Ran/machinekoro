from .cards import LandMarks,CardDex,Card
import random
import time
import json
import math
import copy


# utility functions
def diag_print(content,override=None):
    if override:
        Diag = override
    if Diag:
        print(content)


# global var for debug print
Diag = True


# In-memory Data Obj below
class GameState:
    def __init__(self,player_list):
        # the game evolves by the following cycle
        # ---> get_legal_moves                     advance_state ---> self
        #           |         massage director           |
        #           |____ query > decision > response ___|
        #                     (player or bot)
        # the queries are gathered by get legal moves,
        # send them over channels
        # response is gathered or redirected by the massage director
        # then world is modified during (only during) advance state
        # market is a dict of there lists
        self.market = Market()
        self.tracker = 1
        self.players = player_list
        self.activation = 0
        self.diceroll = []
        # the possible values for phase:
        # pre_roll > post_roll > pre_activation > post_activation > post_card_play > Pre_roll
        self.phase = 'pre_roll'
        self.msg_list = []
        self.humans = 0

    def get_legal_moves(self):
        # this function now returns a query object with intended player, and possible action
        phase = self.phase
        current_player = self.select_current_player()
        if phase == 'pre_roll':
            # returns a query object with allowed dice options
            query = {
                "channel_name": current_player.channel_name,
                "player_num" : current_player.num,
                "q_type":"dice_query_a"
            }
            if current_player.landmark['Train Station'] == 1:
                if current_player.landmark['Moon Tower'] == 1:
                    query['options'] = [1,2,3]
                else:
                    query['options'] = [1,2]
            else:
                query['options'] = [1]
                query['channel_name'] = None # am I allowed to do this? if so None means pipe to advance_state
            return [query]

        elif phase == 'post_roll':
            # returns the  list of queries to active player to choose which diceroll to apply
            query = {
                "channel_name": current_player.channel_name,
                "player_num": current_player.num,
                "q_type": "dice_query_b",
                "options": self.diceroll
            }
            if len(self.diceroll) != 3:
                query['channel_name'] = None
            return [query]

        elif phase == "pre_activation":
            # returns a query asking whether to apply harbour (activation + 2)
            if current_player.landmark['Harbor'] == 1 and self.activation >= 10:
                query = {
                    "channel_name": current_player.channel_name,
                    "player_num": current_player.num,
                    "q_type": "dice_query_c",
                    "options": [True,False]
                }
            else:
                query = {
                    "channel_name": None,
                    "player_num": current_player.num,
                    "q_type": "dice_query_c",
                    "options": [True, False]
                }
            return [query]

        elif phase == 'activation':
            query_list = self.msg_list
            """ If not query list return none
            if not query_list:
                query_list = [{
                    "channel_name": None,
                    "player_num": current_player.num,
                    "q_type": "activation_query",
                    "options": ['Pass']
                }]"""
            return query_list

        elif phase == "post_activation":
            # returns a query object with allowed card play
            coin = current_player.coin
            options = []
            for some_card in self.market.high:
                if coin >= some_card.cost:
                    options.append(some_card.name)
            for some_card in self.market.low:
                if coin >= some_card.cost:
                    options.append(some_card.name)
            for some_card in self.market.purple:
                if coin >= some_card.cost and some_card not in current_player.hand:
                    options.append(some_card.name)
            query_list = [{
                "channel_name": current_player.channel_name,
                "player_num": current_player.num,
                "q_type": "card_play_query",
                "options": options
            }]
            return query_list

        elif phase == "post_card_play":
            # returns query object with tech start-up or whatever
            tSU = Card(CardDex['Tech Start-up'])
            if tSU in current_player.hand and current_player.coin > 0 :
                query_list = [{
                    "channel_name": current_player.channel_name,
                    "player_num": current_player.num,
                    "q_type": "invest_query",
                    "options": [True,False]
                }]
            return query_list
        else:
            pass

    def advance_state(self, query_response_all):
        phase = self.phase
        current_player = self.select_current_player()
        # this method processes query responses and modifies the state NO OUTGOING QUERY FROM HERE!!

        if phase == 'pre_roll':
            for response in query_response_all:
                # rolls dice according to choice
                if response['player_num'] == current_player.num and response['q_type'] == 'dice_query_a':
                    # check if message is the right type and num
                    diceroll = []
                    i = response['choices']
                    n = 0
                    while n < i :
                        diceroll.append(random.choice(range(1,7)))
                        n += 1
                    self.diceroll = diceroll
                else:
                    diag_print("Miss matched query during pre_roll process")
            self.phase = 'post_roll'

        elif phase == 'post_roll':
            # takes a list of query responses and applies all to the state empty snippet
            for response in query_response_all:
                if response['player_num'] == current_player.num and response['q_type'] == 'dice_query_b':
                    choices = response['choices']
                    activation = sum(choices)
                    self.activation = activation
                    self.diceroll = choices
                else:
                    diag_print("Miss matched query during post_roll process")
            self.phase = 'pre_activation'

        elif phase == "pre_activation":
            # takes the query and modify diceroll and and calculates activation
            activation = self.activation
            for response in query_response_all:
                if response['player_num'] == current_player.num and response['q_type'] == 'dice_query_c':
                    choice = response['choices']
                    if choice is False:
                        pass
                    elif choice is True:
                        activation += 2
                    pass
                else:
                    diag_print("Miss matched query during pre_activation process")
            # applies self.activation to all player's hand, collect
            state = self
            query_list = []
            for some_player in self.players:
                if some_player is current_player:
                    # activate cards that are in players hand
                    for card in current_player.hand:
                        if activation in card.activations:
                            query_entry = card.activate(state, current_player, some_player)
                            query_list.append(query_entry)
                else:
                    # process blue and red activations
                    for card in some_player.hand:
                        if activation in card.activations and card.colour in ['Blue', 'Red']:
                            query_entry = card.activate(state, current_player, some_player)
                            query_list.append(query_entry)
            # increment phase tracker
            # save query to massage list
            self.phase = 'activations'
            self.msg_list = query_list

        elif phase == "activation":
            # takes state and query generated from activations and modifies and returns the state
            if query_response_all:
                for response in query_response_all:
                    if response['q_type'] == 'card_query_demo':
                        choice = response['choices']
                        current_player.landmark[choice] = 0
                        current_player.coin += 8
                    elif response['q_type'] == 'card_query_move':
                        card_choice = response['choices'][0]
                        player_choice = self.select_player_by_num(response['choices'][1])
                        for card in current_player.hand and card.name == card_choice:
                            player_choice.hand.append(card)
                            current_player.hand.remove(card)
                            current_player.coin += 4
                    elif response['q_type'] == "card_query_trade":
                        self_choice = response['choices'][0]
                        target_player = self.select_player_by_num(response['choices'][1].key())
                        target_card = response['choices'][1].value()
                        for card in current_player.hand and card.name == self_choice:
                            target_player.hand.append(card)
                            current_player.hand.remove(card)
                        for card in target_player.hand and card.name == target_card:
                            current_player.hand.append(card)
                            target_player.hand.remove(card)
            elif not query_response_all:
                diag_print("No response received advance state without action")
            self.phase = 'post_activation'

        elif phase == "post_activation":
            # takes state and play card action and modifies and returns the state
            # remember to charge for cards
            for response in query_response_all:
                if response['player_num'] == current_player.num and response['q_type'] == 'card_play_query':
                    card_decision = response['choices']
                    card = self.market.pop_card(card_decision)
                    current_player.hand.append(card)
            self.phase = 'post_card_play'

        elif phase == "post_card_play":
            if query_response_all:
                for response in query_response_all:
                    if response['player_num'] == current_player.num and response['q_type'] == 'invest_query':
                        choice = response['choices']
                        # choice to invest 1 coin or not
                        if choice:
                            current_player.snippet += 1
                            current_player.coin -= 1
                        elif not choice:
                            pass
            self.phase = 'pre_roll'

    def select_current_player(self):
        # returns the current player object
        count = len(self.players)
        num = self.tracker % len(self.players)
        if num == 0:
            num == count
        cp = self.select_player_by_num(num)
        return cp

    def select_player_by_num(self,num):
        # returns the player object that matches the specified num
        for some_player in self.players:
            if some_player.num == num:
                return some_player

    @staticmethod
    def check_winner(state):
        winner = None
        for player in state.players:
            landmarks = player.landmark
            if landmarks == {
                    "City Hall":True,
                    "Harbour":True,
                    "Train Station":True,
                    "Shopping Mall":True,
                    "Amusement Park":True,
                    "Moon Tower":True,
                    "Airport":True} :
                winner = player.num
        return winner


class Market:
    def __init__(self):
        self.data = copy.deepcopy(CardDex)
        self.low = []
        self.high = []
        self.purple = []

    def pop_card(self,card_name):
        if card_name in self.low:
            name = self.low.pop(card_name)
            self.replenish_low()
        elif card_name in self.high:
            name = self.high.pop(card_name)
            self.replenish_low()
        elif card_name in self.purple:
            name = self.purple.pop(card_name)
            self.replenish_low()
        card = Card(self.data[name])
        return card

    def replenish_low(self):
        # present 5 low cards, duplicates are stacked and new are drawn
        if len(self.low) < 5:
            l = 5
            while len(self.low) < l:
                choice_data = random.choice(self.data)
                choice = choice_data.value()
                if choice['type'] == 'low' and choice['count'] < choice['limit']:
                    if choice['name'] in self.low:
                        l += 1
                    self.low.append(Card(choice_data))
                    choice['count'] += 1
        else:
            pass

    def replenish_high(self):
        # present 5 high cards, duplicates are stacked and new are drawn
        if len(self.high) < 5:
            l = 5
            while len(self.high) < l:
                choice_data = random.choice(self.data)
                choice = choice_data.value()
                if choice['type'] == 'high' and choice['count'] < choice['limit']:
                    if choice['name'] in self.high:
                        l += 1
                    self.high.append(Card(choice_data))
                    choice['count'] += 1
        else:
            pass

    def replenish_purple(self):
        # present 2 purple cards, duplicates are stacked and new are drawn
        if len(self.purple) < 2:
            l = 2
            while len(self.purple) < l:
                choice_data = random.choice(self.data)
                choice = choice_data.value()
                if choice['type'] == 'purple' and choice['count'] < choice['limit']:
                    if choice['name'] in self.purple:
                        l += 1
                    self.purple.append(Card(choice_data))
                    choice['count'] += 1
        else:
            pass


class Player:
    def __init__(self,num,channel_name=None,name=None):
        self.name = name
        self.num = num
        self.channel_name = channel_name
        self.coin = 3
        self.hand = []
        self.landmark = copy.copy(LandMarks)



# Business/Controller Logic below.

class GameController:
    # game logic lives here, every view cycle, data is loaded from models,
    # processed and saved back to model. the rationale being doing database query for
    # many times during each simulation cycle would be computationally wasteful
    def __init__(self,serial):
        self.serial = serial
        self.db_obj = GameSession(serial=serial,tracker=1)
        self.current_state = []

    def __str__(self):
        return str(self.db_obj)

    # def load_from_db(self,serial):
    # maybe implement for super-users

    def save_player_to_db(self,player,mascot_code=None,):
        game = self.db_obj
        name = player.name
        coin = player.coin
        hand = json.dumps(player.hand)
        landmark = json.dumps(player.landmark)
        player_db = Player_DB(
            name=name,
            coin = coin,
            hand=hand,
            landmark=landmark,
            game = game
        )
        if mascot_code != None:
            player_db.mascot_code = mascot_code
        player_db.save()
        diag_print((str(player.name)+"save to db"))
        pass

    def get_lobby_display(self):
        # this method is for making data obj for the game lobby
        players = Player_DB.objects.filter(game=self.db_obj).order_by('id')
        data = []
        for player in players:
            p = {
                'name' : player.name,
            'mascot' : player.mascot_code # dont forget mascot system hasn't been built
            }
            data.append(p)
        return data


class TreeSearchController:
    # the Core of the program is MCT Search borrowed from Jeff Bradberry,
    # there will be more info but I just want to thank him here first
    def __init__(self, current_state, max_moves=10, max_time=30, c=1.4):
        self.states = [current_state]
        self.wins = {}
        self.plays = {}
        self.C = c  # this is the exploration variable
        self.max_moves = max_moves
        self.max_time = max_time
        self.max_depth = 0

    def update(self,state):
        self.states.append(state)
        pass

    def run_sim(self):
        plays = self.plays
        wins = self.wins
        states_calc = self.states[:]
        state = states_calc[-1]
        visited_states = []
        player = self.game.select_current_player()

        expand = True

        for n in range(1,self.max_moves+1):
            # gets list of legal moves from game controller
            legal_moves = self.game.get_legal_moves(state)
            # the list moves_states below captures all legal next moves and resulting states
            moves_states = [(move,self.game.advance_state(state,move)) for move in legal_moves]

            if all(plays.get((player,state)) for move , state in moves_states):
                # if we have previously visited all legal move states,
                # we can now decide using UCB1 and

                log_total = math.log10(
                    sum(plays[(player, S)] for p, S in moves_states))
                value, move, state = max(
                    ((wins[(player, S)] / plays[(player, S)]) +
                     self.C * math.sqrt(log_total / plays[(player, S)]), p, S)
                    for p, S in moves_states
                )
            else:
                # random decision without state stats
                move, state = random.choice(moves_states)
            states_calc.append(state)

            # expansion stage
            if expand and (player,state) not in self.plays:
                expand = False
                self.plays[(player,state)] = 0
                self.wins[(player,state)] = 0
                if n > self.max_depth:
                    self.max_depth = n

            visited_states.append((player,state))

            player = self.game.select_current_player(state)
            winner = self.game.check_winner(state)
            if winner != 0:
                break

        for player, state in visited_states:
            if (player,state) not in self.plays:
                continue
            self.plays[(player,state)] += 1
            if player == winner:
                self.wins[(player,state)] += 1

    def card_decision(self):
        self.max_depth = 0
        state = self.states[-1]
        player = self.game.select_current_player(state)
        legal_moves = self.game.legal_plays(state)

        # Bail out early if there is no real choice to be made.
        if not legal_moves:
            return None
        if len(legal_moves) == 1:
            return legal_moves[0]

        games = 0
        start = int(time.time())
        while int(time.time()) - start < self.max_time:
            self.run_sim()
            games += 1

        moves_states = [(p, self.game.advance_state(state, p)) for p in legal_moves]

        # Display the number of calls of `run_simulation` and the
        # time elapsed.
        diag_print(('iterations:',str(games),
                    '\ntime elapsed:',str(time.time() - start)))

        # Pick the move with the highest percentage of wins.
        percent_wins, move = max(
            (self.wins.get((player, S), 0) /
             self.plays.get((player, S), 1),
             p)
            for p, S in moves_states
        )

        # Display the stats for each possible play.
        for x in sorted(
                ((100 * self.wins.get((player, S), 0) /
                  self.plays.get((player, S), 1),
                  self.wins.get((player, S), 0),
                  self.plays.get((player, S), 0), p)
                 for p, S in moves_states),
                reverse=True
        ):
            diag_print(
                "{3}: {0:.2f}% ({1} / {2})".format(*x))

        diag_print(
            ("Maximum depth searched:", str(self.max_depth)))

        return move
