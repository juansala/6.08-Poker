import sys
sys.path.append('__HOME__/group')
sys.path.append('__HOME__/Poker')
import sqlite3
import datetime
import requests
import json
from collections import defaultdict

#action=generate&user=salazarj

poker = "__HOME__/Poker/poker.db" # just come up with name of database
score = "__HOME__/Poker/score.db"

# STEPS
# 1. DEAL
# 2. BET_1
# 3. DISCARD
# 4. BET_2
# 5. REVEAL

# Score Keeping DB Functions

def score_database_create():
    conn = sqlite3.connect(score)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)
    c.execute('''CREATE TABLE IF NOT EXISTS poker_score (user text, wins int, losses int);''') # run a CREATE TABLE command
    conn.commit() # commit commands
    conn.close() # close connection to database

def score_database_update(user,win_bool):
    conn = sqlite3.connect(score)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)
    
    exist_user = list(c.execute('''SELECT user FROM poker_score WHERE user = ?''',(user,)))
    
    if len(exist_user) == 0:
            c.execute('''INSERT into poker_score VALUES (?,0,0);''',(user,))
    if win_bool:
            c.execute(""" UPDATE poker_score SET wins = wins + 1 WHERE (user = ?);""",(user,))    
    else:
            c.execute(""" UPDATE poker_score SET losses = losses + 1 WHERE (user = ?);""",(user,)) 
    conn.commit() # commit commands
    conn.close() # close connection to database
    return exist_user

def score_get_table():
    conn = sqlite3.connect(score)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)
    output = c.execute('''SELECT * FROM poker_score;''').fetchall()
    conn.commit() # commit commands
    conn.close() # close connection to database
    return list(output)
                        
# Deck of Cards API

def deal_request(num_cards):
    r = requests.get("""https://deckofcardsapi.com/api/deck/ichox5u6ekat/draw/?count="""+str(num_cards))
    response = json.loads(r.text)
    cards = ''
    cards_arr = response['cards']
    for i in range(len(cards_arr)):
        cards += cards_arr[i]['code']+","
    return cards

def shuffle_deck():
    requests.get("""https://deckofcardsapi.com/api/deck/ichox5u6ekat/shuffle/""")
    return "Reshuffled"

# Poker DB Functions

def poker_database_create():
    conn = sqlite3.connect(poker)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)
    c.execute('''CREATE TABLE IF NOT EXISTS poker_table (started int, user1 text, user2 text, hand1 text, hand2 text, bet1 int, bet2 int, state text, current_player text, winner text);''') # run a CREATE TABLE command
    conn.commit() # commit commands
    conn.close() # close connection to database


def database_startup(user): #POST
    conn = sqlite3.connect(poker)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)
    ante = 2 # initialize ante value
    if len(get_users()) == 0:
        shuffle_deck() # shuffle deck if no users setup
    cards = deal_request(5) # deal 5 cards to a player at the starting round 
    if c.execute('''SELECT * FROM poker_table WHERE started = ?;''', (1,)).fetchone() is None: # if game row is does not exist yet
        c.execute('''INSERT into poker_table VALUES (?,?,?,?,?,?,?,?,?,?);''', (1, user, "", cards, "", 2, 2, "DEAL", user,"None")) # initialize row w/ user1, current player is now user1
    else:
        c.execute('''UPDATE poker_table SET user2 = ?, hand2 = ? WHERE started = ?;''', (user, cards, 1))
    conn.commit() # commit commands
    conn.close() # close connection to database
    return cards

def database_clear():
    conn = sqlite3.connect(poker)
    c = conn.cursor()
    c.execute("""DELETE FROM poker_table;""")    
    conn.commit()
    conn.close()   

def get_database():
    conn = sqlite3.connect(poker)
    c = conn.cursor()
    things = c.execute("""SELECT * FROM poker_table;""").fetchone()   
    conn.commit()
    conn.close()  
    return things

def database_get_table(user): #GET
    conn = sqlite3.connect(poker)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)
    output = c.execute('''SELECT * FROM poker_table WHERE (user1 = ? OR user2 = ?);''',(user,user)).fetchone()
    conn.commit() # commit commands
    conn.close() # close connection to database
    return output
    # return list(output[0]) if len(output) > 0 else []

def database_update_winner(winner):
    conn = sqlite3.connect(poker)
    c = conn.cursor()
    timestamp = datetime.datetime.now()
    users = get_users()
    c.execute(""" UPDATE poker_table SET winner = ? WHERE started = ?;""",(winner, 1)) 
    conn.commit()
    conn.close()

def database_update_hand(user, new_hand):
    conn = sqlite3.connect(poker)
    c = conn.cursor()
    timestamp = datetime.datetime.now()
    users = get_users()
    if user == users[0]:
        c.execute(""" UPDATE poker_table SET hand1 = ? WHERE started = ?;""",(new_hand, 1)) 
    elif user == users[1]:
        c.execute(""" UPDATE poker_table SET hand2 = ? WHERE started = ?;""",(new_hand, 1)) 
    conn.commit()
    conn.close() 
        
def database_update_state(state):
    conn = sqlite3.connect(poker)
    c = conn.cursor()
    timestamp = datetime.datetime.now()
    users = get_users()
    c.execute(""" UPDATE poker_table SET state = ? WHERE started = ?;""",(state, 1)) 
    conn.commit()
    conn.close() 

def database_update_player(user):
    conn = sqlite3.connect(poker)
    c = conn.cursor()
    users = get_users()
    if user == users[0]:
        c.execute(""" UPDATE poker_table SET current_player = ? WHERE started = ?;""",(users[1], 1)) 
    elif user == users[1]:
        c.execute(""" UPDATE poker_table SET current_player = ? WHERE started = ?;""",(users[0], 1))
    conn.commit()
    conn.close() 

def database_update_bet(user, bet, reset=False):
    conn = sqlite3.connect(poker)
    c = conn.cursor()
    timestamp = datetime.datetime.now()
    users = get_users()
    if not reset:
        if user == users[0]:
            c.execute(""" UPDATE poker_table SET bet1 = bet1 + ? WHERE started = ?;""",(bet, 1)) 
        elif user == users[1]:
            c.execute(""" UPDATE poker_table SET bet2 = bet2 + ? WHERE started = ?;""",(bet, 1)) 
    else:
        c.execute(""" UPDATE poker_table SET bet1 = ? WHERE started = ?;""",(2, 1))
        c.execute(""" UPDATE poker_table SET bet2 = ? WHERE started = ?;""",(2, 1))  
    conn.commit()
    conn.close()   

def database_get_pool():
    conn = sqlite3.connect(poker)
    c = conn.cursor()
    bet1 = c.execute(""" SELECT bet1 FROM poker_table WHERE started = ?;""",(1, ))
    bet2 = c.execute(""" SELECT bet2 FROM poker_table WHERE started = ?;""",(1, ))
    conn.commit()
    conn.close()  
    return bet1 + bet2

def database_reset():
    conn = sqlite3.connect(poker)
    c = conn.cursor()
    users = get_users()
    shuffle_deck() # reshuffle deck again
    user1_cards = deal_request(5)
    user2_cards = deal_request(5)
    database_update_hand(users[0], user1_cards) # redeal hand
    database_update_hand(users[1], user2_cards) # redeal hand
    if len(users) >= 2:
        database_update_state("BET_1")
    database_update_bet(None, None, True)
    database_update_winner("None")
    conn.commit()
    conn.close() 

def get_users():
    conn = sqlite3.connect(poker)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)
    things = c.execute('''SELECT * FROM poker_table WHERE started = ?;''', (1,)).fetchone()
    conn.commit()
    conn.close()   
    users = []
    user1 = str(things[1]) if things != None else ''
    user2 = str(things[2]) if things != None else ''
    if len(user1) > 0:
        users.append(user1) # add user1
    if len(user2) > 0:
        users.append(user2) # add user2
    return users

def get_current_hand(user):
    conn = sqlite3.connect(poker)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)
    users = get_users()
    if user == users[0]:
        hand = c.execute('''SELECT hand1 FROM poker_table WHERE started = ?;''', (1,)).fetchone()
    elif user == users[1]:
        hand = c.execute('''SELECT hand2 FROM poker_table WHERE started = ?;''', (1,)).fetchone()
    conn.commit()
    conn.close() 
    return hand[0]

def get_other_hand(user):
    conn = sqlite3.connect(poker)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)
    users = get_users()
    if user == users[0]:
        hand = c.execute('''SELECT hand2 FROM poker_table WHERE started = ?;''', (1,)).fetchone()
    elif user == users[1]:
        hand = c.execute('''SELECT hand1 FROM poker_table WHERE started = ?;''', (1,)).fetchone()
    conn.commit()
    conn.close() 
    return hand[0] if len(hand[0]) > 0 else "None"

def get_current_player():
    conn = sqlite3.connect(poker)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)
    current_player = c.execute('''SELECT current_player FROM poker_table WHERE started = ?;''', (1,)).fetchone()
    conn.commit()
    conn.close() 
    return current_player[0]

def get_state():
    conn = sqlite3.connect(poker)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)
    state = c.execute('''SELECT state FROM poker_table WHERE started = ?;''', (1,)).fetchone()
    conn.commit()
    conn.close() 
    return state[0]

def get_bets(user):
    conn = sqlite3.connect(poker)  # connect to that database (will create if it doesn't already exist)
    users = get_users()
    c = conn.cursor()  # move cursor into database (allows us to execute commands)
    bet1 = c.execute('''SELECT bet1 FROM poker_table WHERE started = ?;''', (1,)).fetchone()
    bet2 = c.execute('''SELECT bet2 FROM poker_table WHERE started = ?;''', (1,)).fetchone()
    conn.commit()
    conn.close() 
    out = ''
    if user == users[0]:
        out = str(bet1[0]) + "," + str(bet2[0]) 
    elif user == users[1]:
        out = str(bet2[0]) + "," +   str(bet1[0])
    return out  

def get_winner():
    conn = sqlite3.connect(poker)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)
    winner = c.execute('''SELECT winner FROM poker_table WHERE started = ?;''', (1,)).fetchone()
    conn.commit()
    conn.close() 
    return winner[0]

def update_scores(user, won): 
    users = get_users()
    if users[0] == user:
        score_database_update(users[0], won)
        score_database_update(users[1], not won)
    else:
        score_database_update(users[1], won)
        score_database_update(users[0], not won)

# Check for Winner - Poker Hand Functions
# Taken from: https://briancaffey.github.io/2018/01/02/checking-poker-hands-with-python.html

card_order_dict = {"2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "T":10,"J":11, "Q":12, "K":13, "A":14}

def check_hand(hand):
    if check_straight_flush(hand):
        return 9
    if check_four_of_a_kind(hand):
        return 8
    if check_full_house(hand):
        return 7
    if check_flush(hand):
        return 6
    if check_straight(hand):
        return 5
    if check_three_of_a_kind(hand):
        return 4
    if check_two_pairs(hand):
        return 3
    if check_one_pairs(hand):
        return 2
    return 1

def check_straight_flush(hand):
    if check_flush(hand) and check_straight(hand):
        return True
    else:
        return False

def check_four_of_a_kind(hand):
    values = [i[0] for i in hand]
    value_counts = defaultdict(lambda:0)
    for v in values: 
        value_counts[v]+=1
    if sorted(value_counts.values()) == [1,4]:
        return True
    return False

def check_full_house(hand):
    values = [i[0] for i in hand]
    value_counts = defaultdict(lambda:0)
    for v in values: 
        value_counts[v]+=1
    if sorted(value_counts.values()) == [2,3]:
        return True
    return False

def check_flush(hand):
    suits = [i[1] for i in hand]
    if len(set(suits))==1:
        return True
    else:
        return False

def check_straight(hand):
    values = [i[0] for i in hand]
    value_counts = defaultdict(lambda:0)
    for v in values:
        value_counts[v] += 1
    rank_values = [card_order_dict[i] for i in values]
    value_range = max(rank_values) - min(rank_values)
    if len(set(value_counts.values())) == 1 and (value_range==4):
        return True
    else: 
        #check straight with low Ace
        if set(values) == set(["A", "2", "3", "4", "5"]):
            return True
        return False

def check_three_of_a_kind(hand):
    values = [i[0] for i in hand]
    value_counts = defaultdict(lambda:0)
    for v in values:
        value_counts[v]+=1
    if set(value_counts.values()) == set([3,1]):
        return True
    else:
        return False

def check_two_pairs(hand):
    values = [i[0] for i in hand]
    value_counts = defaultdict(lambda:0)
    for v in values:
        value_counts[v]+=1
    if sorted(value_counts.values())==[1,2,2]:
        return True
    else:
        return False

def check_one_pairs(hand):
    values = [i[0] for i in hand]
    value_counts = defaultdict(lambda:0)
    for v in values:
        value_counts[v]+=1
    if 2 in value_counts.values():
        return True
    else:
        return False



def request_handler(request):
    poker_database_create()
    score_database_create()
    if request["method"] == "POST": # {action:generate/join/update, user:"username", game:"game"}
            if request["form"]["action"] == "generate":
                user = request["form"]["user"]
                cards = database_startup(user)
                users = get_users()
                if len(users) >= 2:
                    database_update_state("BET_1")

            if request["form"]["action"] == "restart": 
                database_reset() # resets everything to state == BET_1
                users = get_users()

            if request["form"]["action"] == "fold": 
                user = request["form"]["user"]
                users = get_users()
                update_scores(user, False)
                winner = users[1] if user == users[0] else users[0] 
                database_update_winner(winner)
                database_update_state("REVEAL")
                
            if request["form"]["action"] == "bet":
                user = request["form"]["user"]
                bet = str(request["form"]["value"])
                database_update_bet(user, bet)
                database_update_player(user)
                users = get_users()
                if user == users[1] :
                    if get_state() == "BET_1":
                        database_update_state("DISCARD")
                    elif get_state() == "BET_2":
                        database_update_state("REVEAL")

            if request["form"]["action"] == "leave":
                # clear the table for everyone, poker game's over for tonight
                user = request["form"]["user"]
                update_scores(user, False)
                database_clear()

            if request["form"]["action"] == "discard":   
                # update existing player's hand, respond with new hand
                user = request["form"]["user"]
                discarded_cards = request["form"]["cards"].split(",") # expects string of discarded cards, then splits it to get individual cards
                # return request["form"]["cards"]
                if len(request["form"]["cards"]) > 0:
                    new_cards = deal_request(len(discarded_cards))
                    new_cards = new_cards.split(",")
                    current_cards = get_current_hand(user)
                    temp = current_cards
                    for i in range(len(discarded_cards)):
                        current_cards = temp.replace(discarded_cards[i], new_cards[i], 1) # replace one card at a time
                        temp = current_cards
                    database_update_hand(user, current_cards)
                database_update_player(user)
                users = get_users()
                if user == users[1]:
                    database_update_state("BET_2")
                

    if request["method"] == "GET":
        # respond with CURRENT_PLAYER,GAME_STATE, ...

            # DEBUGGING GET REQUESTS

            if "debug" in request["args"]:
                table = get_database()
                return table
            if "debug_table" in request["args"]:
                table = database_get_table
                return table
            if "debug_users" in request["args"]:
                users = get_users()
                return users
            if "debug_score" in request["args"]:
                table = score_get_table()
                return table
            if "debug_current_player" in request["args"]:
                current_player = get_current_player()
                return current_player
            if "debug_score" in request["args"]:
                return score_get_all()
            if "debug_cards" in request["args"]:
                users = get_users()
                database_update_hand(users[0], "0, 0, 0, 0, 0")
            if "clear" in request["args"]:
                database_clear()
            if "debug_current_cards" in request["args"]:
                user = request["values"]["debug_current_cards"]
                hand = get_current_hand(user)
                new_hand = hand.replace("0", "T")
                new_hand = new_hand.replace("1", "")
                new_hand = new_hand.split(",")
                return new_hand[0:len(hand)-1]
            if "debug_deal" in request["args"]:
                cards = deal_request(5)
                return cards
            if "shuffle" in request["args"]:
                shuffle_deck()
            if "debug_update_player" in request["args"]:
                user = request["values"]["debug_update_player"]
                database_update_player(user)
            if "debug_update_state" in request["args"]:
                state = request["values"]["debug_update_state"]
                return database_update_state(state)
            if "debug_winner" in request["args"]:
                return get_winner()
                # database_update_winner("TEST")

            if "debug_poker_results" in request["args"]:
                users = get_users()
                user1_hand = get_current_hand(users[0])    # Processing to adjust to the borrowed poker eval code
                user1_hand = user1_hand.replace("0", "T")
                # user1_hand = user1_hand.replace("1", "")
                user1_hand = user1_hand.split(",")

                user2_hand = get_current_hand(users[1])
                user2_hand = user2_hand.replace("0", "T")
                # user2_hand = user2_hand.replace("1", "")
                user2_hand = user2_hand.split(",")

                user1_result = check_hand(user1_hand[0:len(user1_hand)-1])
                user2_result = check_hand(user2_hand[0:len(user2_hand)-1])

                return (user1_result, user2_result)

            # GAME GET REQUESTS
            
            if "get" in request["args"]:
                user = request["values"]["get"]
                output = get_database() #[started, user1, user2, hand1, hand2, bet1, bet2, state, current_player, winner]
                if output == []:
                    return "NONE,GAME OVER"
                else:
                    # Return game info: CURRENT_PLAYER|CURRENT_HAND|OTHER_HAND|STATE|BET1|BET2|WINNER
                    current_player = get_current_player()
                    current_hand = get_current_hand(user)
                    state = get_state()
                    winner = get_winner()
                    users = get_users()

                    if state == "REVEAL":
                        user1_hand = get_current_hand(users[0])    # Processing to adjust to the borrowed poker eval code
                        user1_hand = user1_hand.replace("0", "T")
                        # user1_hand = user1_hand.replace("1", "")
                        user1_hand = user1_hand.split(",")

                        user2_hand = get_current_hand(users[1])
                        user2_hand = user2_hand.replace("0", "T")
                        # user2_hand = user2_hand.replace("1", "")
                        user2_hand = user2_hand.split(",")

                        user1_result = check_hand(user1_hand[0:len(user1_hand)-1])
                        user2_result = check_hand(user2_hand[0:len(user2_hand)-1])
                        if winner == "None":
                            if user1_result > user2_result:
                                winner = users[0]
                            elif user1_result == user2_result:
                                winner = "None"
                            else:
                                winner = users[1]
                            database_update_winner(winner) # logic to determine winner, then update database only if winner hasn't already been determined and updated                       

                    # both hands are always returned, other player's hand hidden on ESP32 until the REVEAL state
                    return get_current_player() + "|" + get_current_hand(user) + "|" + get_other_hand(user) + "|" + get_state() + "|" + get_bets(user) + "|" + get_winner() + "|"


