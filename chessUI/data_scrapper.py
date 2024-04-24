import lichess.api
import berserk
import time
import requests

game_id = 'tn5IGFmk'
file_path = 'moves.txt'
USER_API_TOKEN = 'lip_HaJoxjLLofX2FRgDJlBD'
turn = 'white'
prev_size = 0



def get_game_moves(game_id):
    game = lichess.api.game(game_id)
    moves = game['moves']
    return moves

def save_moves_to_file(moves, file_path):
    with open(file_path, 'w') as file:
        for move in moves:
            file.write(move)

# Function to create a new game with a bot
def create_new_game_with_bot():
    # Parameters for creating a new game
    username = "automatechessmate"
    rated = False  # Set to True for a rated game, False for an unrated game
    clock_limit = 3
    clock_increment = 3
    days = 0
    color = "random"  # Choose color randomly (can also be "white" or "black")
    variant = "standard"  # Chess variant (standard, chess960, etc.)
    token = "lip_OOb8ZjPb0XzdGP8tL6Zz" # bots token
    level= 3  # Bot level (ranges from 1 to 8, with 1 being the easiest and 8 being the hardest)
    response = client.challenges.create_with_accept(username=username, rated=rated, token=token, clock_limit=180, clock_increment=20, days = None, color = 'white', variant=variant, position=None)
    game_id = response['challenge']['id']
    return game_id


if __name__ == "__main__":
    session = berserk.TokenSession(USER_API_TOKEN)
    client = berserk.Client(session=session)
    game_id = create_new_game_with_bot()
    print(game_id)
    time.sleep(2)
    moves = ['g1f3', 'g2g3', 'f1g2', 'e1g1', 'd2d3', 'b1d2', 'd1e1' ]
    #'e2e4', 'd2d3', 

    for move in moves:
        time.sleep(1)
        response = client.board.make_move(game_id, move)
        moves = get_game_moves(game_id)
        save_moves_to_file(moves, file_path)
        print("Moves updated.")
        time.sleep(25)  # Wait for 60 seconds before fetching moves again
    client.board.resign_game(game_id)