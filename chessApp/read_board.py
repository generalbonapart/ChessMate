import threading
import socket
import time
import RPi_I2C_driver
from chess_board import convert_move_to_board_notation
from lichess_api import add_user_move, get_bot_move, is_game_active, game_status, move_accepted, is_move_legal, get_time_left
from board_detection import board_detection_init, get_user_move, report_bot_move
from models import GameParams
import RPi.GPIO as GPIO

HOST = '127.0.0.1'  # Localhost
PORT = 65432        # Port to listen on
sock = None
previous_move = "a8a8"

def convert_seconds_to_min_sec(seconds: int):
    # Calculate minutes and remaining seconds
    minutes, sec = divmod(seconds, 60)
    # Format the string as min:sec with leading zeros for seconds if needed
    return f"{minutes}:{sec:02}"


def lcd_thread(time):

    print(time)
    mylcd = RPi_I2C_driver.lcd()
    # Set the GPIO mode
    GPIO.setmode(GPIO.BCM)
    # Set up the button pin as an input with a pull-up resistor
    GPIO.setup(RPi_I2C_driver.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    while is_game_active():
        white_seconds, black_seconds = get_time_left()
        if not white_seconds:
            white_seconds = time
        if not black_seconds:
            black_seconds = time

        white_time = convert_seconds_to_min_sec(white_seconds)
        black_time = convert_seconds_to_min_sec(black_seconds)

        mylcd.lcd_display_string("    White      Black", 1)
        mylcd.lcd_display_string(f"    {white_time}      {black_time}", 3)

        time.sleep(0.1)
        mylcd.lcd_clear()

    mylcd.lcd_clear()
    mylcd.lcd_display_string_pos("Game Over", 2, 5)
    time.sleep(2)
    mylcd.lcd_clear()
    mylcd.backlight(0)
    GPIO.cleanup()

def main_thread():
    global previous_move
    conn, addr = sock.accept()
    #with conn:
    print(f'Connected by {addr}')
    time.sleep(1)
    while is_game_active():
        # i = input("Press r when move is done, q to exit")
        # if i== 'q':
        #     user_move = 'q'
        # else:
        #     user_move = get_user_move()
        user_move = input("User move: ")
        # Read the button status
        while(GPIO.input(RPi_I2C_driver.BUTTON_PIN) != GPIO.LOW):
            time.sleep(0.1)
            
        add_user_move(user_move)
        previous_move = user_move
        if user_move == 'q':
            conn.sendall(user_move.encode())
            break
        #time.sleep(0.1)
        move_accepted.wait()
        move_accepted.clear()

        if is_move_legal():
            bot_move = None
            while(bot_move is None or bot_move == previous_move):
                time.sleep(1)
                bot_move = get_bot_move()
                
            previous_move = bot_move
            print("Bot's move: ", bot_move)
            #report_bot_move(bot_move)
            conn.sendall(bot_move.encode())
            # Block until the trolley has done its job
            ack = conn.recv(1024).decode('utf-8')
            print(ack)
        else:
            print(f"Illegal move {user_move}")

    sock.close()


def init_board_control(time):
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()
    thread1 = threading.Thread(target=main_thread)
    thread2 = threading.Thread(target=lcd_thread, args=(time, ))
    thread1.start()
    thread2.start()
    board_detection_init()

if __name__ == "__main__":
    init_board_control()

