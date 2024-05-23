# Save this as script.py
import sys
import json
import lichess.api
import berserk
import time
import requests
import threading
import csv
import queue
from __future__ import print_function # In python 2.7
import sys

file_path = 'moves.txt'
USER_API_TOKEN = 'lip_HaJoxjLLofX2FRgDJlBD' #'lip_HaJoxjLLofX2FRgDJlBD'
BOT_API_TOKEN = 'lip_aug0ace9zXdcNrcIfRhL'
URL = 'https://lichess.org/'
game_not_over = True
user_move_index = 0
user_moves = queue.Queue()
#move_history = ["start"]
lock = threading.Lock()
game_id = ''

def send_challenge(chess_parameters):
    global game_id
    parameters = {
    "clock_limit": 180,         # Time limit for each player in seconds
    "clock_increment": 20,      # Time increment per move in seconds
    "days": None,               # Number of days the challenge is valid (None for no limit)
    "color": "white",          # Choose color randomly (can also be "white" or "black")
    "variant": "standard",      # Chess variant (standard, chess960, etc.)
    "level" : "2"
    }
    # parameters = {
    # "clock_limit": chess_parameters['clock_limit'],         # Time limit for each player in seconds
    # "clock_increment": chess_parameters['clock_increment'],      # Time increment per move in seconds
    # "days": None,               # Number of days the challenge is valid (None for no limit)
    # "color": chess_parameters['color'],          # Choose color randomly (can also be "white" or "black")
    # "variant": chess_parameters['variant'],      # Chess variant (standard, chess960, etc.)
    # "level" : chess_parameters['level']
    # }
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
        # print(f"---Move History is {move_history}")     
        # for update in client.board.stream_incoming_events():
        #     if update["game"]:
        #         last_move = update["game"]["lastMove"]
        #         if(last_move and (move_history[-1] != last_move)):
        #             move_history.append(last_move)
        #             with open('game_history.csv', 'w', newline='') as file:
        #                 writer = csv.writer(file) 
        #                 writer.writerow([last_move])
        #             time.sleep(1)
        #             break
            #time.sleep(1)
    # lock.release()
    # time.sleep(3)                


def post_user_moves(stop_threads):
    global game_id, game_not_over, lock
    while(game_not_over):
        if stop_threads():
            break
        
        for update in client.board.stream_incoming_events():
            if (is_my_turn(update) and not user_moves.empty() and game_not_over):
                print(f"Posting Move {user_moves.queue[0]}")
                client.board.make_move(game_id,user_moves.get())
                time.sleep(5)
                break
            time.sleep(3)
    time.sleep(2)


def add_moves_to_queue(input_user_moves, stop_threads):
    global user_move_index, game_not_over
    while((user_move_index < len(input_user_moves)) and game_not_over):
        if stop_threads():
            break
        move_history = get_game_moves(game_id)
        
        #update move history file asap
        with open('game_history.csv', 'w', newline='') as file:
            writer = csv.writer(file) 
            writer.writerow([move_history])
        user_moves.put(input_user_moves[user_move_index])
        print("Q so far :", user_moves.queue[0])
        user_move_index += 1
        time.sleep(2)
    
def clear_file(file_path):
    with open(file_path, 'w') as file:
        file.truncate(0)
    print(f"Contents of {file_path} have been deleted.")



if __name__ == "__main__":
    print("inside script.py!!!")
    input_str = sys.argv[1]
    chess_parameters = json.dumps(input_str)
    # Process the input data
    result = f"Received input: {chess_parameters}"
    

    session = berserk.TokenSession(USER_API_TOKEN)
    client = berserk.Client(session=session)
    clear_file('game_history.csv')
    input_user_moves = ['g1f3', 'g2g3', 'f1g2', 'e1g1', 'd2d3', 'b1d2', 'd1e1','h2h3','g1h2','a2a3', 'b2b3', 'c1b2','d2c4' ]
    send_challenge(chess_parameters)
    # stop_threads = False
    # thread_post_moves = threading.Thread(target=post_user_moves, args=(lambda: stop_threads, ))
    # thread_save_moves_to_csv = threading.Thread(target=add_last_move_to_csv, args=(lambda: stop_threads, ) )
    # thread_take_user_input = threading.Thread(target=add_moves_to_queue, args=(input_user_moves,lambda: stop_threads, ))
    
    # print("Starting thread: save moves to csv")
    # thread_save_moves_to_csv.start()
    # print("Starting thread: take user input")
    # thread_take_user_input.start()
    # print("Starting thread: post moves")
    # thread_post_moves.start()
    

    # while(game_not_over):
    #     for update in client.board.stream_game_state(game_id):
    #         status = handle_game_state_update(update)
    #         game_not_over = False if status in ['draw', 'mate', 'resign', 'outoftime'] else True
    #         time.sleep(3)
    #         break
    #     time.sleep(3)
    # print("Game Over!")

    # stop_threads = True

    
    # if thread_post_moves.is_alive():
    #     print("Thread 1 is still running")
    # else:
    #     print("Thread 1 has finished")

    # if thread_take_user_input.is_alive():
    #     print("Thread 2 is still running")
    # else:
    #     print("Thread 2 has finished")

    # if thread_save_moves_to_csv.is_alive():
    #     print("Thread 3 is still running")
    # else:
    #     print("Thread 3 has finished")

    # thread_post_moves.join()
    # thread_take_user_input.join()
    # thread_save_moves_to_csv.join()

