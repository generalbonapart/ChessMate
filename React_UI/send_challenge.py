import lichess.api
import berserk
import time
import requests
import threading
import csv
import queue
import json
import sys

file_path = 'moves.txt'
USER_API_TOKEN = 'lip_aug0ace9zXdcNrcIfRhL'
BOT_API_TOKEN = 'lip_OOb8ZjPb0XzdGP8tL6Zz'
URL = 'https://lichess.org/'
game_not_over = True
user_move_index = 0
user_moves = queue.Queue()
updates_queue = queue.Queue()
lock = threading.Lock()
game_id = ''


#Doc: https://berserk.readthedocs.io/en/master/api.html#module-berserk.clients

def get_update():
    for update in client.board.stream_incoming_events():
        if update["game"]:
            return

# Function to create a new game with a bot
def send_challenge(input_params):
    global game_id

    #uncomment below parameters{...} if send_challenge.py is executed individually

    # parameters = {
    # "clock_limit":180,         # Time limit for each player in seconds
    # "clock_increment": 10,      # Time increment per move in seconds
    # "days": None,               # Number of days the challenge is valid (None for no limit)
    # "color": "white",          # Choose color randomly (can also be "white" or "black")
    # "variant": "standard",      # Chess variant (standard, chess960, etc.)
    # "level" : "3"
    # }

    # Uncomment below parameters if send_challenge.py is executed via nextJS UI
    parameters = {
    "clock_limit":int(input_params['clock_limit']),         # Time limit for each player in seconds
    "clock_increment": int(input_params['clock_increment']),      # Time increment per move in seconds
    "days": None,               # Number of days the challenge is valid (None for no limit)
    "color": str(input_params['color']),          # Choose color randomly (can also be "white" or "black")
    "variant": str(input_params['variant']),      # Chess variant (standard, chess960, etc.)
    "level" : str(input_params['level'])
    }
    response = client.challenges.create_ai(**parameters)  # Challenge is issued against level x stockengine
    
    print(response)
    game_id = response['id']
    visit_gameURL(game_id)                   #Throws an error if invalid URL
    return game_id

def resign_game():
    global game_id
    try:
        response = client.board.resign_game(game_id)
        if response.status_code == 200:
            print("Successfully resigned game : ", game_id)
        else:
            print("Failed to resign game:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("Error:", e)

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

def stream_game_moves():
    # Stream game moves
    for event in client.games.stream_game_moves(game_id):
        if 'fen' in event:
            moves = event['fen']
            print(f"Moves: {moves}")
            return moves
        time.sleep(1)

def get_game_moves(game_id):
    for event in client.board.stream_game_state(game_id):
        if 'state' in event:
            moves = event['state']['moves']
            time.sleep(6)
            return moves
        

# Function to handle game state updates
# Use stream_board_gamestate()
def handle_game_state_update(update):
    if update["state"]:
       return update["state"]["status"]
    


def is_my_turn(update):
    if update["game"]:
        return update["game"]["isMyTurn"]
    else:
        return False

def add_last_move_to_csv(stop_threads): 
    global game_not_over, move_history, game_id
    # lock.acquire()
    while(game_not_over): 
        if stop_threads():
            break
        move_history = get_game_moves(game_id)
        with open('game_history.csv', 'w', newline='') as file:
            writer = csv.writer(file) 
            writer.writerow([move_history])
        time.sleep(1)
           


def post_user_moves(stop_threads):
    global game_id, game_not_over, lock
    while(game_not_over):
        if stop_threads():
            break

        for update in client.board.stream_incoming_events():
            if (is_my_turn(update) and not user_moves.empty() and game_not_over):
                print(f"Posting Move {user_moves.queue[0]}")
                client.board.make_move(game_id,user_moves.get())
                break
            time.sleep(3)
        time.sleep(3)


def add_moves_to_queue(input_user_moves, stop_threads):
    global user_move_index, game_not_over
    while((user_move_index < len(input_user_moves)) and game_not_over):
        if stop_threads():
            break

        user_moves.put(input_user_moves[user_move_index])
        print("Q so far :", user_moves.queue[0])
        user_move_index += 1
        time.sleep(1)
    
def clear_file(file_path):
    with open(file_path, 'w') as file:
        file.truncate(0)
    print(f"Contents of {file_path} have been deleted.")

def args_to_dict(args):
    arg_dict = {}
    for arg in args:
        if ':' in arg:
            key, value = arg.split(': ')
            arg_dict[key] = value
    return arg_dict

def system_args_to_dict():
    input_argv = sys.argv[1:]
    s = str(input_argv)
    s = s[2:-2]
    r = s.replace("'", '"')
    j = json.loads(r)
    return j

if __name__ == "__main__":
    session = berserk.TokenSession(USER_API_TOKEN)
    client = berserk.Client(session=session)
    
    
    command_line_args = sys.argv[1:]
    input_params = system_args_to_dict()
    clear_file('game_history.csv')
    input_user_moves = ['g1f3', 'g2g3', 'f1g2', 'e1g1', 'd2d3', 'b1d2', 'd1e1','h2h3','g1h2','a2a3', 'b2b3', 'c1b2','d2c4' ]
    send_challenge(input_params)
    stop_threads = False
    thread_post_moves = threading.Thread(target=post_user_moves, args=(lambda: stop_threads, ))
    thread_save_moves_to_csv = threading.Thread(target=add_last_move_to_csv, args=(lambda: stop_threads, ) )
    thread_take_user_input = threading.Thread(target=add_moves_to_queue, args=(input_user_moves,lambda: stop_threads, ))
    
    print("Starting thread: save moves to csv")
    thread_save_moves_to_csv.start()
    print("Starting thread: take user input")
    thread_take_user_input.start()
    print("Starting thread: post moves")
    thread_post_moves.start()
    

    while(game_not_over):
        for update in client.board.stream_game_state(game_id):
            status = handle_game_state_update(update)
            game_not_over = False if status in ['draw', 'mate', 'resign', 'outoftime'] else True
            time.sleep(3)
            break
        time.sleep(3)
    print("Game Over!")

    stop_threads = True

    
    if thread_post_moves.is_alive():
        print("Thread 1 is still running")
    else:
        print("Thread 1 has finished")

    if thread_take_user_input.is_alive():
        print("Thread 2 is still running")
    else:
        print("Thread 2 has finished")

    if thread_save_moves_to_csv.is_alive():
        print("Thread 3 is still running")
    else:
        print("Thread 3 has finished")

    thread_post_moves.join()
    thread_take_user_input.join()
    thread_save_moves_to_csv.join()



    