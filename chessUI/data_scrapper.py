import lichess.api
import berserk
import time



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
    parameters = {
        "rated": True,  # Set to True for a rated game, False for an unrated game
        "variant": "standard",  # Chess variant (standard, chess960, etc.)
        "timeControl": "180+2",  # Time control in seconds (180 seconds initial time + 2 seconds increment)
        "color": "random",  # Choose color randomly (can also be "white" or "black")
        "level": 3  # Bot level (ranges from 1 to 8, with 1 being the easiest and 8 being the hardest)
    }

    #response = client.bots.
    #game_id = response['challenge']['id']
    return game_id


if __name__ == "__main__":
    game_id = 'tn5IGFmk'
    file_path = 'moves.txt'
    API_TOKEN = 'lip_HaJoxjLLofX2FRgDJlBD'
    session = berserk.TokenSession(API_TOKEN)
    client = berserk.Client(session=session)
    game_id = create_new_game_with_bot()

    print(game_id)

    while False:
        moves = get_game_moves(game_id)
        save_moves_to_file(moves, file_path)
        print("Moves updated.")
        time.sleep(2)  # Wait for 60 seconds before fetching moves again