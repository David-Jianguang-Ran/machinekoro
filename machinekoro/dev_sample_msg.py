# this file contains the various massages used in the program
# no code in this file will or should be executed, it is purely for human readability of the over-all program

# note that the actual message recived could have extra attributes due the being passed in various layers

# action query sample gameprocessor > prime player > player consumer > client
query_list = [{
    'key': "action.query",
    "player_num": 'player.num',
    "q_type": "invest_query",
    "options": [True, False],
    "only_option":'bool'
}]
