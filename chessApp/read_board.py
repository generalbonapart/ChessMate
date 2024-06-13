import threading
import socket
import time
from chess_board import convert_move_to_board_notation
from lichess_api import add_user_move, get_game_moves

HOST = '127.0.0.1'  # Localhost
PORT = 65432        # Port to listen on
sock = None
previous_move = "a8a8"

def main_thread():
    global previous_move
    conn, addr = sock.accept()
    #with conn:
    print(f'Connected by {addr}')
    while True:
        
        time.sleep(1)
        user_move = input("User move: ")
        add_user_move(user_move)
        previous_move = user_move

        bot_move = None
        while(bot_move is None or bot_move == previous_move):
            time.sleep(1)
            bot_move = get_game_moves()
            
        previous_move = bot_move
        print("Bot's move: ", bot_move)
        conn.sendall(bot_move.encode())

def init_board_control():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()
    thread = threading.Thread(target=main_thread)
    thread.start()
            

if __name__ == "__main__":
    init_board_control()

