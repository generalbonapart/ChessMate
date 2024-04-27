import lichess.api
import berserk
import time
import requests
import threading
import csv
import queue

file_path = 'moves.txt'
USER_API_TOKEN = 'lip_HaJoxjLLofX2FRgDJlBD'
BOT_API_TOKEN = 'lip_OOb8ZjPb0XzdGP8tL6Zz'
URL = 'https://lichess.org/'
game_not_over = True
user_move_index = 0
user_moves = queue.Queue()
move_history = ["start"]
lock = threading.Lock()
game_id = ''


#Doc: https://berserk.readthedocs.io/en/master/api.html#module-berserk.clients



# Function to create a new game with a bot
def send_challenge():
    global game_id
    parameters = {
    "clock_limit": 180,         # Time limit for each player in seconds
    "clock_increment": 20,      # Time increment per move in seconds
    "days": None,               # Number of days the challenge is valid (None for no limit)
    "color": "white",          # Choose color randomly (can also be "white" or "black")
    "variant": "standard",      # Chess variant (standard, chess960, etc.)
    "level" : "2"
    }
    response = client.challenges.create_ai(**parameters)  # Challenge is issued against level x stockengine
    game_id = response['id']
    visit_gameURL(game_id)                   #Throws an error if invalid URL
    return game_id

def visit_gameURL(game_id):
    url = URL+game_id
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Successfully visited the URL:", response.url)
        else:
            print("Failed to visit the URL:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("Error:", e)

def get_game_moves(game_id):
    game = lichess.api.game(game_id)
    return game['moves']

# Function to handle game state updates
# Use stream_board_gamestate()
def handle_game_state_update(update):
    if update["state"]:
       return update["state"]["status"]
    
# use stream_incoming_events()
def get_color(update):
    if update["game"] :
        return update["game"]["color"]

#stream incoming events
# def add_last_move_to_csv():
#     lock.acquire()
#     while(game_not_over):
#         print("----------inside csv function ----------------")
#         for update in client.board.stream_incoming_events():
#             if update["game"]:
#                 with open('game_history.csv', 'w', newline='') as file:
#                     curr_move = [update["game"]["lastMove"]]
#                     if(curr_move and move_history[-1] != curr_move):
#                         move_history.append(curr_move)
#                         writer = csv.writer(file)
#                         writer.writerow(curr_move)
#         time.sleep(2)
#     lock.release()

# use stream_incoming_events()
def is_my_turn(update):
    if update["game"]:
        return update["game"]["isMyTurn"]
    else:
        return False
    
def post_user_moves():
    global game_id, game_not_over, lock
    lock.acquire() 
    while(game_not_over):        
        for update in client.board.stream_incoming_events():
            if (is_my_turn(update) and not user_moves.empty() and game_not_over):
                time.sleep(5)
                print(f"Posting Move {user_moves.queue[0]}")
                client.board.make_move(game_id,user_moves.get())
                break
    time.sleep(2)
    lock.release()

def add_moves_to_queue(input_user_moves):
    print("Inside add moves-----------")
    global user_move_index, game_not_over
    while((user_move_index < len(input_user_moves)) and game_not_over):
        user_moves.put(input_user_moves[user_move_index])
        print("Q so far :", user_moves.queue[0])
        user_move_index += 1
        time.sleep(3)
    




if __name__ == "__main__":
    session = berserk.TokenSession(USER_API_TOKEN)
    client = berserk.Client(session=session)
    input_user_moves = ['g1f3', 'g2g3', 'f1g2', 'e1g1', 'd2d3', 'b1d2', 'd1e1' ]
    send_challenge()
    T1 = threading.Thread(target=post_user_moves)
    # T2 = threading.Thread(target=add_last_move_to_csv)
    T3 = threading.Thread(target=add_moves_to_queue, args=(input_user_moves,))
    
    T3.start()
    print("-------------between--------------")
    T1.start()

    # add logic to end both threads
    while(game_not_over):
        for update in client.board.stream_game_state(game_id):
            status = handle_game_state_update(update)
            game_not_over = False if status in ['draw', 'mate', 'resign', 'outoftime'] else True
            break
        time.sleep(1)
    print("Game Over!")


    if T1.is_alive():
        print("Thread 1 is still running")
    else:
        print("Thread 1 has finished")

    if T3.is_alive():
        print("Thread 3 is still running")
    else:
        print("Thread 3 has finished")
    
    T1.join()
    T3.join()
    # T2.join()


    