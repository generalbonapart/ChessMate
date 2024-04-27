import lichess.api
import berserk
import time
import requests
import threading
import csv

file_path = 'moves.txt'
USER_API_TOKEN = 'lip_HaJoxjLLofX2FRgDJlBD'
BOT_API_TOKEN = 'lip_OOb8ZjPb0XzdGP8tL6Zz'
URL = 'https://lichess.org/'
turn = 'white'
prev_size = 0
game_moves = ['game_started']
lock = threading.Lock()


#Doc: https://berserk.readthedocs.io/en/master/api.html#module-berserk.clients

def get_game_moves(game_id):
    game = lichess.api.game(game_id)
    moves = game['moves']
    return moves

def save_moves_to_file(moves, file_path):
    with open(file_path, 'w') as file:
        for move in moves:
            file.write(move)

# Function to create a new game with a bot
def send_challenge():
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
    print(game_id)
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

#might need some rework to save individual moves in every row
def save_moveCSV(move):  
    csv_file = 'output.csv'
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([move])

def get_last_move(moves):
    last_move = ""
    index = len(moves)-1 #will this work with -1

    while index >=0 and moves[index] !=" ":
        last_move = moves[index]+last_move
        index -= 1
    return last_move



def start_the_game():
    print("1: Game Started!")
    moves = ['g1f3', 'g2g3', 'f1g2', 'e1g1', 'd2d3', 'b1d2', 'd1e1' ] 
    client.board.make_move(game_id, moves[0]) # make the first move
    print("-----------Making first move! ---------")
    index = 1
    game_not_over = True
    while(game_not_over):
        if(len(game_moves) > 1 and (len(game_moves)%2 ==0)):
            client.board.make_move(game_id,moves[index])
            time.sleep(3)
            if(index < len(moves)-1):
                index+=1
            print("1: User Move Sent!")
        for update in client.board.stream_game_state(game_id):
            status = handle_game_state_update(update)
            print("----------", status)
            game_not_over = False if status in ['draw', 'mate', 'resign', 'outoftime'] else True
        time.sleep(5)
    client.board.resign_game(game_id)
    game_not_over = False
    print("1: Thread start the game stopped")

# Function to handle game state updates
def handle_game_state_update(update):
    if update["type"] == "gameState":
        status = update['status']
        return status
    

def get_color(update):
    if update["game"] :
        return update["game"]["color"]


def update_game_moves():
    #constantly check if move history is updated 
    #add new moves instantly to game_moves
    game_not_over = True
    while(game_not_over):
        print("2: Updating Game Moves!")
        move_history = get_game_moves(game_id)
        print("2: Move History: ", move_history)
        last_move = str(get_last_move(move_history))
        print("2: Last Move: ", last_move)
        if((last_move) and (last_move != game_moves[-1])):
            game_moves.append(last_move)
            print("2: Appending last game move")
        #game_not_over = True if game_state['status'] in ['draw', 'mate', 'resign', 'outoftime'] else False
        for update in client.board.stream_game_state(game_id):
            status = handle_game_state_update(update)
            game_not_over = False if status in ['draw', 'mate', 'resign', 'outoftime'] else True
        
        #for update in client.board.stream_incoming_events():
            #print(get_color(update))
        print("Stored Game Moves:", game_moves)
    print("2: Thread update game moves stopped!")


if __name__ == "__main__":
    session = berserk.TokenSession(USER_API_TOKEN)
    client = berserk.Client(session=session)
    
    thread = threading.Thread(target=update_game_moves )
    thread2 = threading.Thread(target=start_the_game, daemon=True)
    game_id = send_challenge() #to stockfish
    thread.start()
    thread2.start()
    thread.join()
    thread2.join()