import copy
import random
import json

# the info on the game is on http://machi-koro.wikia.com/wiki/Machi_Koro_Wiki
# hard coded card index, this data is used to initialize a card obj that gets added to the players hand
# landmark card index is below
# landmark logic entangled in the game logic sorry~

# I need to verify that all landmark logic has been implemented! Check off below

LandMarks = {
    "City Hall":True, # Check
    "Harbour":False,  # Check
    "Train Station":False,  # Check
    "Shopping Mall":False,  # Check
    "Amusement Park":False, # Check
    "Moon Tower":False,  # Check
    "Airport":False # Check
}

CardDex = {
    "Wheat Field": {
        "name": "Wheat Field",
        "colour": "Blue",
        'type': "low",
        'cost': 1,
        'activations': [1],
        'limit':6,
        'count':0
    },
    "Ranch": {
        "name": "Ranch",
        "colour": "Blue",
        'type': "low",
        'cost': 1,
        'activations': [2],
        'limit':6,
        'count':0
    },
    "Flower Orchard": {
        "name": "Flower Orchard",
        "colour": "Blue",
        'type': "low",
        'cost': 2,
        'activations': [4],
        'limit':6,
        'count':0
    },
    "Forrest": {
        "name": "Forrest",
        "colour": "Blue",
        'type': "low",
        'cost': 3,
        'activations': [5],
        'limit':6,
        'count':0
    },
    "Mackerel Boat": {
        "name": "Mackerel Boat",
        "colour": "Blue",
        'type': "high",
        'cost': 2,
        'activations': [8],
        'limit':6,
        'count':0
    },
    "Apple Orchard": {
        "name": "Apple Orchard",
        "colour": "Blue",
        'type': "high",
        'cost': 3,
        'activations': [10],
        'limit':6,
        'count':0
    },
    "Tuna Boat": {
        "name": "Tuna Boat",
        "colour": "Blue",
        'type': "high",
        'cost': 5,
        'activations': [12, 13, 14],
        'limit':6,
        'count':0
    },
    "General Store": {
        "name": "General Store",
        "colour": "Green",
        'type': "low",
        'cost': 0,
        'activations': [2],
        'limit':6,
        'count':0
    },
    "Bakery": {
        "name": "Bakery",
        "colour": "Green",
        'type': "low",
        'cost': 1,
        'activations': [2,3],
        'limit': 6,
        'count':0
    },
    "Demolition Company": {
        "name": "Demolition Company",
        "colour": "Green",
        'type': "low",
        'cost': 2,
        'activations': [4],
        'limit': 6,
        'count':0
    },
    "Flower Shop": {
        "name": "Flower Shop",
        "colour": "Green",
        'type': "low",
        'cost': 2,
        'activations': [2],
        'limit': 6,
        'count':0
    },
    "Cheese Factory": {
        "name": "Cheese Factory",
        "colour": "Green",
        'type': "high",
        'cost': 5,
        'activations': [7],
        'limit': 6,
        'count':0
    },
    "Furniture Factory": {
        "name": "Furniture Factory",
        "colour": "Green",
        'type': "high",
        'cost': 3,
        'activations': [8],
        'limit': 6,
        'count':0
    },
    "Moving Company": {
        "name": "Moving Company",
        "colour": "Green",
        'type': "high",
        'cost': 2,
        'activations': [9,10],
        'limit': 6,
        'count':0
    },
    "Soda Bottling Plant": {
        "name": "Soda Bottling Plant",
        "colour": "Green",
        'type': "high",
        'cost': 5,
        'activations': [11],
        'limit': 6,
        'count':0
    },
    "Farmers Market": {
        "name": "Farmers Market",
        "colour": "Green",
        'type': "high",
        'cost': 2,
        'activations': [11, 12],
        'limit': 6,
        'count':0
    },
    "Sushi Bar": {
        "name": "Sushi Bar",
        "colour": "Red",
        'type': "low",
        'cost': 2,
        'activations': [1],
        'limit': 6,
        'count':0
    },
    "Cafe": {
        "name": "Cafe",
        "colour": "Red",
        'type': "low",
        'cost': 2,
        'activations': [3],
        'limit': 6,
        'count':0
    },
    "French Restaurant": {
        "name": "French Restaurant",
        "colour": "Red",
        'type': "low",
        'cost': 2,
        'activations': [1],
        'limit': 6,
        'count':0
    },
    "Family Restaurant": {
        "name": "Family Restaurant",
        "colour": "Red",
        'type': "high",
        'cost': 3,
        'activations': [9,10],
        'limit': 6,
        'count':0
    },
    "Member's Only Club": {
        "name": "Members Only Club",
        "colour": "Red",
        'type': "high",
        'cost': 4,
        'activations': [12, 14],
        'limit': 6,
        'count':0
    },
    "Pizza Joint": {
        "name": "Pizza Joint",
        "colour": "Red",
        'type': "high",
        'cost': 1,
        'activations': [7],
        'limit': 6,
        'count':0
    },
    "Business Center": {
        "name": "Business Center",
        "colour": "Purple",
        'type': "Purple",
        'cost': 8,
        'activations': [6],
        'limit': 6,
        'count':0
    },
    "Stadium": {
        "name": "Stadium",
        "colour": "Purple",
        'type': "Purple",
        'cost': 6,
        'activations': [6],
        'limit': 6,
        'count':0
    },
    "Publisher": {
        "name": "Publisher",
        "colour": "Purple",
        'type': "Purple",
        'cost': 5,
        'activations': [7],
        'limit': 6,
        'count':0
    },
    "Tax Office": {
        "name": "Business Center",
        "colour": "Purple",
        'type': "Purple",
        'cost': 4,
        'activations': [8,9],
        'limit': 6,
        'count':0
    },
    "Tech Start-up": {
        "name": "Tech Start-up",
        "colour": "Purple",
        'type': "Purple",
        'cost': 1,
        'activations': [10],
        'limit': 6,
        'count':0
    },
}


class GameState:
    """
    This object is deliberately small since many instances of state will be saved to memory and data
    all functions that modify this state are stored in the GameController object
    GameController.current_state = state <- THIS OBJECT

    O attributes:

    - tracker : {
        active_player :
        phase :
        # the possible values for phase:
        # pre_roll > post_roll > pre_activation > post_activation > post_card_play > Pre_roll
    }

    - market : {
        deck_info :
        low :
        high :
    }

    - players : {
        num : {
            coin : int
            landmark: landmark dict
            hand:  list of cards
         }
         num 2 : {
            ...
         }
    }
    """
    def __init__(self,player_count=None,json_set=None):
        if json_set:
            self.tracker = json.loads(json_set['tracker'])
            self.market = json.loads(json_set['market'])
            self.players = json.loads(json_set['players'])
            self.temp_data = json.loads(json_set['temp_data'])

        elif player_count:
            self.tracker = {
                'active_player_num': 0,
                'phase': 'pre_roll',
                'winner': None
            }
            self.market = {
                'deck_info': copy.deepcopy(CardDex),
                'low': {},
                'high': {},
                'purple': {}
            }
            self.players = {}
            for i in range(0,player_count):
                self.players[str(i)] = {
                    'num_str': str(i),
                    'coin': 3,
                    'landmark': LandMarks,
                    'hand': ['Wheat Field','Bakery'],
                    'snippet': None
                }
            self.temp_data = {}

    # something would probably go wrong here check NoteW@73
    # will the json of this obj still have self.temp_data?
    def __str__(self):
        """
        This method has been overwritten to exclude temp_data in prints and comparisons
        :return:
        """
        dict_representation = self.__dict__
        dict_representation.pop('temp_data')
        return str(dict_representation)

    def __eq__(self, other):
        """
        This method has been overwritten for comparing states
        :return:
        """
        return self.__str__ == other.__str__


class Card:
    """
    This object is instanced when GameController is running resolve_activation
    This will not be saved to state (state saves only card name)
    """
    def __init__(self,name):
        self.name = name

    def __str__(self):
        return str(self.name)

    @ staticmethod
    def __take_away_coin(taker,giver,amount):
        """
        This method transfer coins equal to amount from giver to taker.
        if giver has less then amount, giver gives what ever he has
        :param taker: player obj
        :param giver: player obj
        :param amount: int
        :return: None
        """
        if giver.coin >= amount:
            giver.coin -= amount
            taker.coin += amount
        elif giver.coin >= 0:
            taker.coin += giver.coin
            giver.coin = 0

    def activate(self, state, active_player, current_player=None):
        """
        # this method as all the actions of all regular cards
        # when it is called it will look up the name of the card calling and modify the world appropriately
        :param state: the state to be modified
        :param active_player:
        :param current_player: if there is no current player , that means it is activating the prime player's hand
        :return:
        """
        if self.name in ['Wheat Field','Ranch','Flower Orchard','Forrest']:
            active_player.coin += 1

        elif self.name == 'Bakery':
            active_player.coin += 1
            if active_player.landmark['Shopping Mall']:
                active_player.coin += 1

        elif self.name == 'Apple Orchard':
            active_player.coin += 3

        elif self.name == "Mackerel Boat" and active_player.landmark["Harbor"]:
            active_player.coin += 3

        elif self.name == 'Tuna Boat' and active_player.landmark['Harbor']:
            a = random.choice(range(1,7))
            b = random.choice(range(1,7))
            active_player.coin = a + b + active_player.coin

        elif self.name == 'General Store':
            landmarks = active_player.landmark
            total = 0
            amount = 2
            if active_player.landmark['Shopping Mall']:
                amount = 3
            for entry in landmarks:
                total += entry.value()
            if total < 2:
                active_player.coin += amount

        elif self.name == 'Demolition Company':
            landmarks = active_player.landmark
            total = 0
            keys = []
            for entry in landmarks:
                total += entry.value()
                if entry.value() != 0 and entry.key() != 'City Hall':
                    keys.append(entry.key())
            if total > 1:
                query = {
                    "key": "action.query",
                    "player_num": current_player.num,
                    "q_type": "card_query_demo",
                    'options': keys,
                }
                if len(query['options']) == 1:
                    query['only_option'] = True
                return query

        elif self.name == 'Flower Shop':
            count = 0
            for card in active_player.hand:
                if card.name == 'Flower Orchard':
                    count += 1
            active_player.coin += count

        elif self.name == 'Cheese Factory':
            count = 0
            for card in active_player.hand:
                if card.name == 'Ranch':
                    count += 1
            active_player.coin += count * 3

        elif self.name == 'Furniture Factory':
            count = 0
            for card in active_player.hand:
                if card.name == 'Forrest':
                    count += 1
            active_player.coin += count * 3

        elif self.name == 'Moving Company':
            names = []
            target = []
            # make list of num for possible card recipient
            for some_player in state.players:
                if some_player is active_player:
                    pass
                else:
                    target.append(some_player.num)
            # make list of possible card to give
            for card in active_player.hand :
                if card.colour != 'Purple':
                    names.append(card.name)
            query = {
                "key": "action.query",
                "player_num": active_player.num,
                "q_type": "card_query_move",
                'options': [names,target],
            }
            if len(names) == 1 and len(target) == 1:
                query['only_option'] = True
            return query

        elif self.name == 'Soda Bottling Plant':
            count = 0
            for active_player in state.players:
                for card in active_player.hand:
                    if card.colour == "Red":
                        count += 1
            active_player.coin += count

        elif self.name == 'Farmers Market':
            count = 0
            for card in active_player.hand:
                if card.name in ['Wheat Field','Flower Orchard','Apple Orchard']:
                    count += 1
            active_player.coin += count * 2

        elif self.name == 'Sushi Bar' and active_player.landmark['Harbor'] == 1:
            amount = 3
            if active_player.landmark['Shopping Mall']:
                amount += 1
            self.__take_away_coin(current_player,active_player,amount)

        elif self.name in ['Cafe','Pizza Joint']:
            amount = 1
            if active_player.landmark['Shopping Mall']:
                amount += 1
            self.__take_away_coin(current_player,active_player,amount)

        elif self.name == 'French Restaurant' :
            amount = 5
            if active_player.landmark['Shopping Mall']:
                amount += 1

            landmarks = current_player.landmark
            total = 0
            for entry in landmarks:
                total += entry.value()
            if total >= 2:
                self.__take_away_coin(current_player, active_player, amount)

        elif self.name == 'Family Restaurant':
            amount = 2
            if active_player.landmark['Shopping Mall']:
                amount += 1

            self.__take_away_coin(current_player,active_player,amount)

        elif self.name == 'Members Only Club' :
            landmarks = current_player.landmark
            total = 0
            for entry in landmarks:
                total += entry.value()
            if total >= 3:
                active_player.coin += current_player.coin
                current_player.coin = 0

        elif self.name == 'Publisher':
            for some_player in state.players:
                p_count = 0
                for card in active_player.hand:
                    if card.color == "Red" or card.name in ['Bakery','Flower Shop','General Store']:
                        p_count += 1
                self.__take_away_coin(active_player,some_player,p_count)

        elif self.name == 'Stadium':
            for some_player in state.players:
                self.__take_away_coin(active_player,some_player,2)

        elif self.name == 'Tax Office':
            for some_player in state.players:
                if some_player.coin >= 10:
                    count = some_player.coin // 2
                    some_player.coin -= count
                    active_player.coin += count

        elif self.name == 'Business Center':
            choice_s = []
            for card in active_player.hand:
                choice_s.append(card.name)
            choice_t = []
            for some_player in state.players:
                if some_player.num == active_player.num:
                    pass
                else:
                    hand_copy = []
                    for some_card in some_player.hand:
                        if some_card.colour != 'Purple':
                            hand_copy.append(some_card.name)
                    entry = {
                        some_player.num : hand_copy
                    }
                    choice_t.append(entry)
            query = {
                "key": "action.query",
                "player_num": active_player.num,
                "q_type": "card_query_trade",
                'options': [choice_s,choice_t],
            }
            return query

        elif self.name == "Tech Start-up":
            amount = active_player.snippet
            for some_player in state.players:
                self.__take_away_coin(active_player,some_player,amount)

        else:
            print(str(self) + 'Not activated due to unsatisfied condition')
            pass

