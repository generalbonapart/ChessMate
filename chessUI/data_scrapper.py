import lichess.api
import time

def get_game_moves(game_id):
    game = lichess.api.game(game_id)
    moves = game['moves']
    return moves

def save_moves_to_file(moves, file_path):
    with open(file_path, 'w') as file:
        for move in moves:
            file.write(move)

if __name__ == "__main__":
    game_id = 'tn5IGFmk'
    file_path = 'moves.txt'
    
    while True:
        moves = get_game_moves(game_id)
        save_moves_to_file(moves, file_path)
        print("Moves updated.")
        time.sleep(2)  # Wait for 60 seconds before fetching moves again