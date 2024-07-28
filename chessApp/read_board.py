import threading
from time import sleep
import RPi_I2C_driver
from RPi import GPIO
from lichess_api import add_user_move, get_bot_move, is_game_active, get_game_status, move_accepted, is_move_legal, get_time_left
from board_detection import board_detection_init, get_user_move, report_bot_move
from chess_board import *
from models import GameParams
from trolley import *

previous_move = "a8a8"
trolley = None
mylcd = None
illegal_move = False

def convert_seconds_to_min_sec(seconds: int):
    # Calculate minutes and remaining seconds
    minutes, sec = divmod(seconds, 60)
    # Format the string as min:sec with leading zeros for seconds if needed
    return f"{minutes}:{sec:02}"

def lcd_init():
    global mylcd
    if mylcd is None:
        mylcd = RPi_I2C_driver.lcd()
    
def lcd_display_key(lcd_secret):
    lcd_init()
    mylcd.lcd_display_secret_key(lcd_secret)

def lcd_illegal_move(move):
    mylcd.lcd_clear()
    mylcd.lcd_display_string(f"{move} is illegal", 1)
    mylcd.lcd_display_string("Make a new move", 3)
    
def buttons_init():
    # Set the GPIO mode
    GPIO.setmode(GPIO.BCM)
    # Set up the button pin as an input with a pull-up resistor
    GPIO.setup(RPi_I2C_driver.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
def lcd_thread(time):
    global mylcd, illegal_move
    mylcd.lcd_clear()
    
    while is_game_active():
        if illegal_move:
            lcd_illegal_move(previous_move)
        else:
            white_seconds, black_seconds = get_time_left()
            if not white_seconds:
                white_seconds = time
            if not black_seconds:
                black_seconds = time

            white_time = convert_seconds_to_min_sec(white_seconds)
            black_time = convert_seconds_to_min_sec(black_seconds)

            mylcd.lcd_display_chess_time(white_time, black_time)
        sleep(0.1)

    mylcd.lcd_clear()
    mylcd.lcd_display_string_pos(get_game_status(), 2, 5)
    sleep(5)
    mylcd.lcd_clear()
    mylcd.lcd_display_string("Start new game", 2)

def main_thread():
    global previous_move, trolley, illegal_move
    sleep(1)
    while is_game_active():
        
        # Read the button status
        while(GPIO.input(RPi_I2C_driver.BUTTON_PIN) != GPIO.LOW):
            sleep(0.1)
        
        if illegal_move:
            illegal_move = False
            mylcd.lcd_clear()
            
        user_move = get_user_move()
        feedback = input(f'{user_move} ? ')
        if feedback == 'y':
            pass
        else:
            user_move = feedback
        #user_move = input("User move: ")

        add_user_move(user_move)
        previous_move = user_move
        if user_move == 'q':
            break
            
        move_accepted.wait()
        move_accepted.clear()
        
        if is_move_legal():
            chess_board_inst.move_piece_string(user_move)
            bot_move = None
            while(bot_move is None or bot_move == previous_move):
                sleep(1)
                bot_move = get_bot_move()
                
            previous_move = bot_move
            print("Bot's move: ", bot_move)
            report_bot_move(bot_move)
            trolley.make_move(bot_move)
        else:
            illegal_move = True
            print(f"Illegal move {user_move}")
            lcd_illegal_move(user_move)
    
    trolley.take_initial_position()

def init_trolley():
    global trolley
    if trolley is None:
        trolley = Trolley()
    
def init_board_control(time):
    lcd_init()
    buttons_init()
    init_trolley()
    thread1 = threading.Thread(target=main_thread)
    thread2 = threading.Thread(target=lcd_thread, args=(time, ))
    thread1.start()
    thread2.start()
    board_detection_init()


if __name__ == "__main__":
    init_board_control()

