import lichess.api
import berserk
import time
import requests
import threading
import csv
import json
from swagger_server.models.game_params import GameParams
from swagger_server.my_token import USER_API_TOKEN
# Monkey-patch requests to avoid using simplejson
from requests.models import Response
def patched_json(self, **kwargs):
    return json.loads(self.text, **kwargs)
Response.json = patched_json

moves_string = ''
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
        "clock_increment": 5,      # Time increment per move in seconds
        "days": None,               # Number of days the challenge is valid (None for no limit)
        "color": params.side,           # Choose color randomly (can also be "white" or "black")
        "variant": "standard",      # Chess variant (standard, chess960, etc.)
        "level": params.level                 # AI level (1-8)
    }
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
def get_game_moves():
    return moves_string

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

# Function to add the last move to a CSV file
def add_last_move_to_csv():
    move_history = get_game_moves()
    with open('game_history.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([move_history])
    return move_history

# Function to post user moves
def post_user_moves(stop_threads):
    global game_not_over, user_move
    while game_not_over:
        if stop_threads():
            break
        for update in client.board.stream_incoming_events():
            if is_my_turn(update) and game_not_over:
                move_history = get_game_moves()
                if move_history:
                    print(move_history)
                
                #move = input("Enter your move (e.g., e2e4): ")
                while not user_move:
                    print("Waiting for move")
                    time.sleep(1)
                if user_move == 'q':
                    resign_game()
                    game_not_over = False
                    break
                print(f"Posting Move {user_move}")
                client.board.make_move(game_id, user_move)
                user_move = None
                break
        time.sleep(3)

def main_thread():
    global client, game_not_over, moves_string
    while game_not_over:
        for update in client.board.stream_game_state(game_id):
            moves_string = update['state']['moves']
            status = handle_game_state_update(update)
            game_not_over = False if status in ['draw', 'mate', 'resign', 'outoftime'] else True
            time.sleep(5)
            break
    time.sleep(3)

    print("Game Over!")
    game_not_over = True
    client = None

# Function to clear the contents of a file
def clear_file(file_path):
    with open(file_path, 'w') as file:
        file.truncate(0)
    print(f"Contents of {file_path} have been deleted.")

def launch_game(parameters: GameParams):
    session = berserk.TokenSession(USER_API_TOKEN)
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