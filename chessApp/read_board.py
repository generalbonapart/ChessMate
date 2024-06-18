import threading
import socket
import time
from chess_board import convert_move_to_board_notation
from lichess_api import add_user_move, get_bot_move, game_not_over, game_status, move_accepted
from board_detection import board_detection_init, get_user_move, report_bot_move
HOST = '127.0.0.1'  # Localhost
PORT = 65432        # Port to listen on
sock = None
previous_move = "a8a8"

def main_thread():
    global previous_move
    conn, addr = sock.accept()
    #with conn:
    print(f'Connected by {addr}')
    time.sleep(1)
    while game_not_over:
        i = input("Press r when move is done, q to exit")
        if i== 'q':
            user_move = 'q'
        else:
            user_move = get_user_move()
            #user_move = input("User move: ")
            add_user_move(user_move)
            previous_move = user_move
            
        while move_accepted is None:
            time.sleep(0.01)
        
        if move_accepted:
            bot_move = None
            while(bot_move is None or bot_move == previous_move):
                time.sleep(1)
                bot_move = get_bot_move()
                
            previous_move = bot_move
            print("Bot's move: ", bot_move)
            report_bot_move(bot_move)
            conn.sendall(bot_move.encode())
            # Block until the trolley has done its job
            ack = conn.recv(1024).decode('utf-8')
            print(ack)
        else:
            print(f"Illegal move {user_move}")

def init_board_control():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()
    thread = threading.Thread(target=main_thread)
    thread.start()
    board_detection_init()

if __name__ == "__main__":
    init_board_control()

