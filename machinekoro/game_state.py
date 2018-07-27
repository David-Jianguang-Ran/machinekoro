import copy
import random

from .cards import LandMarks, CardDex, Card


# In-memory Data Obj below
class GameState:
    """
    this obj records the game state and has methods to process legal state changes
     the game evolves by the following cycle
     ---> get_legal_moves                     advance_state ---> self
               |         massage director           |
               |____ query > decision > response ___|
                         (player or bot)
     the queries are gathered by get legal moves,
     send them over channels
     response is gathered or redirected by the massage director
     then world is modified during (only during) advance state
     market is a dict of there lists """
    def __init__(self, player_list, market=None, tracker=None):
        self.players = player_list
        self.activation = 0
        # add active player
        self.diceroll = []
        # the possible values for phase:
        # pre_roll > post_roll > pre_activation > post_activation > post_card_play > Pre_roll
        self.msg_list = []

        # load existing market
        if market:
            self.market = market
        else:
            self.market = Market()

        # load from tracker
        if tracker:
            self.hand_count = tracker['hand_count']
            self.phase = tracker['phase']
        else:
            self.hand_count = 1
            self.phase = 'pre_roll'

    def get_legal_moves(self):
        # this function now returns a query object with intended player, and possible action
        phase = self.phase
        current_player = self.select_current_player()
        if phase == 'pre_roll':
            # returns a query object with allowed dice options
            query = {
                "key" : "action.query",
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
                query['only_option'] = True
            return [query]

        elif phase == 'post_roll':
            # returns the  list of queries to active player to choose which diceroll to apply
            query = {
                "key": "action.query",
                "player_num": current_player.num,
                "q_type": "dice_query_b",
                "options": self.diceroll
            }
            if len(self.diceroll) != 3:
                query['only_option'] = True
            return [query]

        elif phase == "pre_activation":
            # returns a query asking whether to apply harbour (activation + 2)
            if current_player.landmark['Harbor'] == 1 and self.activation >= 10:
                query = {
                    "key": "action.query",
                    "player_num": current_player.num,
                    "q_type": "dice_query_c",
                    "options": [True,False]
                }
            else:
                query = {
                    "key": "action.query",
                    "player_num": current_player.num,
                    "q_type": "dice_query_c",
                    "options": [True, False],
                    "only_option" : True
                }
            return [query]

        elif phase == 'activation':
            query_list = self.msg_list
            # ??? what the hell is this? what does this do?
            # answer: no query is prepared here because query from card activation must be generated
            # when the card action is applied, therefore here we only copy queries from an attribute and return them
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
                "key" : "action.query" ,
                "player_num" : current_player.num,
                "q_type": "card_play_query",
                "options": options
            }]
            return query_list

        elif phase == "post_card_play":
            # returns query object with tech start-up or whatever
            tSU = Card(CardDex['Tech Start-up'])
            if tSU in current_player.hand and current_player.coin > 0 :
                query_list = [{
                    "key" : "action.query" ,
                    "player_num" : current_player.num,
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
                    print("Miss matched query during pre_roll process")
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
                    print("Miss matched query during post_roll process")
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
                    print("Miss matched query during pre_activation process")
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
                print("No response received advance state without action")
            self.phase = 'post_activation'

        elif phase == "post_activation":
            # takes state and play card action and modifies and returns the state
            # remember to charge for cards!!!
            for response in query_response_all:
                if response['player_num'] == current_player.num and response['q_type'] == 'card_play_query':
                    card_decision = response['choices']
                    choice_card = Card(CardDex[card_decision])
                    if current_player.coin >= choice_card.cost:
                        card = self.market.pop_card(card_decision)
                        current_player.coin -= card.cost
                        current_player.hand.append(card)
                    else:
                        print("WARNING: Card Cost error detected")
            self.phase = 'post_card_play'

        elif phase == "post_card_play":
            if query_response_all:
                for response in query_response_all:
                    if response['player_num'] == current_player.num and response['q_type'] == 'invest_query':
                        choice = response['choices']
                        # choice to invest 1 coin or not
                        if choice:
                            current_player.investment += 1
                            current_player.coin -= 1
                        elif not choice:
                            pass
            self.phase = 'pre_roll'
            self.hand_count += 1

    def select_current_player(self):
        # returns the current player object
        count = len(self.players)
        num = self.hand_count % len(self.players)
        if num == 0:
            num = count
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
                    "City Hall": True,
                    "Harbour": True,
                    "Train Station": True,
                    "Shopping Mall": True,
                    "Amusement Park": True,
                    "Moon Tower": True,
                    "Airport": True}:
                winner = player.num
        return winner


class Market:
    """ this obj records the state of the marketplace, the card repo that all players draw from
    method to replenish cards and handle player 'build' actions"""
    def __init__(self):
        self.data = copy.deepcopy(CardDex)
        self.low = []
        self.high = []
        self.purple = []

    def pop_card(self,card_name):
        # card_name passed in here has been validated in advance_state
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
    """ in memory obj used to keep track of player status"""
    def __init__(self,num):
        self.num = num
        self.coin = 3
        self.hand = []
        self.landmark = copy.copy(LandMarks)
        self.investment = []

    """
    -defecated method- (gross!)
    def stringyfy_hand(self):
        str_hand = [str(x) for x in self.hand]
        self.hand = str_hand
        return self
    """

