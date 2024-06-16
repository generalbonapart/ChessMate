import lichess.api
import berserk
import time
import requests
import threading
import csv
import json
from models import GameParams

# Monkey-patch requests to avoid using simplejson
from requests.models import Response
def patched_json(self, **kwargs):
    return json.loads(self.text, **kwargs)
Response.json = patched_json

URL = 'https://lichess.org/'
game_not_over = True
user_move = None
game_id = None
client = None

# Function to create a new game with a bot
def send_challenge(params: GameParams):
    global game_id

    parameters = {
        "clock_limit": params.time,         # Time limit for each player in seconds
        "clock_increment": params.time_inc,      # Time increment per move in seconds
        "days": None,               # Number of days the challenge is valid (None for no limit)
        "color": params.side,           # Choose color randomly (can also be "white" or "black")
        "variant": "standard",      # Chess variant (standard, chess960, etc.)
        "level": params.level                 # AI level (1-8)
    }
    print(parameters)
    response = client.challenges.create_ai(**parameters)
    game_id = response['id']
    visit_gameURL(game_id)

# Function to resign from the game
def resign_game():
    try:
        client.board.resign_game(game_id)
    except requests.exceptions.RequestException as e:
        print("Error:", e)

# Function to visit the game URL
def visit_gameURL(game_id):
    url = URL + game_id
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Successfully visited the URL:", response.url)
        else:
            print("Failed to visit the URL:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("Error:", e)

# Function to get game moves
def get_bot_move():
    last = None
    for event in client.board.stream_game_state(game_id):
        if 'state' in event:
            moves = event['state']['moves']
            if moves:
                last = moves.split()[-1]
            return last

def add_user_move(move):
    global user_move
    user_move = move

# Function to handle game state updates
def handle_game_state_update(update):
    if update["state"]:
        return update["state"]["status"]

# Function to check if it's the player's turn
def is_my_turn(update):
    if update["game"]:
        return update["game"]["isMyTurn"]
    return False

# Function to post user moves
def post_user_moves(stop_threads):
    global game_not_over, user_move
    while game_not_over:
        if stop_threads():
            break
        for update in client.board.stream_incoming_events():
            if is_my_turn(update) and game_not_over:

                while not user_move:
                    time.sleep(0.01)
                if user_move == 'q':
                    resign_game()
                    game_not_over = False
                    break
                #print(f"Posting Move {user_move}\n")
                try:
                    client.board.make_move(game_id, user_move)
                except:
                    pass
                user_move = None
                break
        time.sleep(3)

def main_thread():
    global client, game_not_over
    while game_not_over:
        for update in client.board.stream_game_state(game_id):
            status = handle_game_state_update(update)
            game_not_over = False if status in ['draw', 'mate', 'resign', 'outoftime'] else True
            break
        time.sleep(1)

    time.sleep(3)
    print("Game Over!")
    game_not_over = True
    client = None

def launch_game(parameters: GameParams, user_api_token):
    session = berserk.TokenSession(user_api_token)
    global client
    client = berserk.Client(session=session)
    send_challenge(parameters)
    stop_threads = False
    thread_post_moves = threading.Thread(target=post_user_moves, args=(lambda: stop_threads, ))
    thread_main_game = threading.Thread(target=main_thread)

    print("Starting game")
    thread_post_moves.start()
    thread_main_game.start()


if __name__ == "__main__":
    launch_game()