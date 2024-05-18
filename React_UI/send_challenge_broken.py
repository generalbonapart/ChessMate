import lichess.api
import berserk
import time
import requests
import threading
import csv
import queue

file_path = 'moves.txt'
USER_API_TOKEN = 'lip_aug0ace9zXdcNrcIfRhL'
BOT_API_TOKEN = 'lip_OOb8ZjPb0XzdGP8tL6Zz'
URL = 'https://lichess.org/'
game_not_over = True
user_move_index = 0
user_moves = queue.Queue()
event_queue = queue.Queue()
#move_history = ["start"]
lock = threading.Lock()
game_id = ''
update = None




#Doc: https://berserk.readthedocs.io/en/master/api.html#module-berserk.clients

def set_update(updt):
    global update
    update = updt

def event_stream_thread(event_queue: queue, stop_threads,):
    global update
    while game_not_over:
        if stop_threads.is_set():
            return
        for u in client.board.stream_incoming_events():
            event_queue.put(u)

        if not event_queue.empty():
            update = event_queue.get()
        time.sleep(7)
        



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

def get_game_moves(game_id):
    game = lichess.api.game(game_id)
    return game['moves']

# Function to handle game state updates
# Use stream_board_gamestate()
def handle_game_state_update(update):
    if update["state"]:
       return update["state"]["status"]
    
def write_to_file():
    global game_not_over, move_history, game_id
    move_history = get_game_moves(game_id)
    with open('game_history.csv', 'w', newline='') as file:
        writer = csv.writer(file) 
        writer.writerow([move_history])


def is_my_turn(update):
    # if update["game"]:
    #     return update["game"]["isMyTurn"]
    # else:
    #     return False
    print("My turn is: ", update["isMyTurn"])
    return update["isMyTurn"]

def add_last_move_to_csv(stop_threads): 
    global game_not_over, move_history, game_id
    # lock.acquire()
    while(game_not_over): 
        if stop_threads.is_set():
            return
        write_to_file()
        time.sleep(1)

def post_user_moves(stop_threads):
    global game_id, game_not_over,update
    while(game_not_over):
        if stop_threads.is_set():
            return
        # if not update:
        #     print("No update registered so far!")
        #     break
        update = client.board.stream_incoming_events()
        if (is_my_turn(update["game"]) and not user_moves.empty() and game_not_over):
            print(f"Posting Move {user_moves.queue[0]}")
            client.board.make_move(game_id,user_moves.get())
            time.sleep(5)
            break
        time.sleep(1)


def add_moves_to_queue(input_user_moves,stop_threads):
    global user_move_index, game_not_over
    while((user_move_index < len(input_user_moves)) and game_not_over):
        if stop_threads.is_set():
            return     
        write_to_file()
        user_moves.put(input_user_moves[user_move_index])
        print("Q so far :", user_moves.queue[0])
        user_move_index += 1
        time.sleep(1)
    
def clear_file(file_path):
    with open(file_path, 'w') as file:
        file.truncate(0)
    print(f"Contents of {file_path} have been deleted.")

def game_not_over_check(stop_threads):
    global game_not_over, update
    while(game_not_over):
        status = handle_game_state_update(update)
        game_not_over = False if status in ['draw', 'mate', 'resign', 'outoftime'] else True
        time.sleep(2)
    stop_threads.set()
    print("Game Over")
    return

if __name__ == "__main__":
    session = berserk.TokenSession(USER_API_TOKEN)
    client = berserk.Client(session=session)
    # updt = client.board.stream_incoming_events()
    
    clear_file('game_history.csv')
    input_user_moves = ['g1f3', 'g2g3', 'f1g2', 'e1g1', 'd2d3', 'b1d2', 'd1e1','h2h3','g1h2','a2a3', 'b2b3', 'c1b2','d2c4' ]
    send_challenge()
    # set_update(updt)
    stop_threads = threading.Event()
    thread_post_moves = threading.Thread(target=post_user_moves, args=(stop_threads, ))
    thread_save_moves_to_csv = threading.Thread(target=add_last_move_to_csv, args=( stop_threads, ) )
    thread_take_user_input = threading.Thread(target=add_moves_to_queue, args=(input_user_moves,stop_threads, ))
    # stream_thread = threading.Thread(target=event_stream_thread, args=(event_queue, stop_threads,))
    # game_over_thread = threading.Thread(target=game_not_over_check, args=(stop_threads, ))
    
    # print("Starting thread: stream thread")
    # stream_thread.start()
    print("Starting thread: save moves to csv")
    thread_save_moves_to_csv.start()
    print("Starting thread: take user input")
    thread_take_user_input.start()
    print("Starting thread: post moves")
    thread_post_moves.start()
    # print("Starting thread: game not over")
    # game_over_thread.start()
    


    
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
    # stream_thread.join()
    # game_over_thread.join()



    