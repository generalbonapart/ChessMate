import sys
import time
from TMC2209.src.TMC_2209_StepperDriver import *
from RPi import GPIO

# Pins assignment
MAGNET_PIN = 18

ENABLE0_PIN = 21
STEP0_PIN = 16
DIR0_PIN = 20

ENABLE1_PIN = 26
STEP1_PIN = 13
DIR1_PIN = 19

# Define variables for aDir, bDir, aPower, bPower
aDir = 0
bDir = 1
aPower = 2
bPower = 3

SQUARE_STEP = 510
DIAG_STEP = 1020

class Trolley:

    # Motor control settings [aDir, bDir, aPower, bPower]
    MOTOR_DIREC = {
        "XLEFT": [-1, 1, 1, 1],
        "XRIGHT": [1, -1, 1, 1],
        "YDOWN": [-1, -1, 1, 1],
        "YUP": [1, 1, 1, 1],
        "DDOWNL": [-1, -1, 1, 0],
        "DDOWNR": [-1, 1, 0, 1],
        "DUPL": [-1, -1, 0, 1],
        "DUPR": [1, -1, 1, 0]
    }

    class Move:
        def __init__(self, startX, startY, endX, endY):
            self.startX = startX
            self.startY = startY
            self.endX = endX
            self.endY = endY

    def __init__(self, free_speed = 1000, free_acceleration = 1000, loaded_speed = 500, loaded_acceleration = 300):

        self.free_speed = free_speed
        self.free_acceleration = free_acceleration
        self.loaded_speed = loaded_speed
        self.loaded_acceleration = loaded_acceleration
        self.currentX = 0
        self.currentY = 0
        self.stallguard_threshold = 200

        # Pin Setup for ElectroMagnet
        GPIO.setmode(GPIO.BCM)  
        GPIO.setup(MAGNET_PIN, GPIO.OUT)  
        self.magnet_OFF()

        # Set up the 2 Core XY motors
        self.tmc1 = TMC_2209(ENABLE0_PIN, STEP0_PIN, DIR0_PIN, driver_address=0)
        self.tmc2 = TMC_2209(ENABLE1_PIN, STEP1_PIN, DIR1_PIN, driver_address=1)

        for tmc in [self.tmc1, self.tmc2]:

            tmc.tmc_logger.set_loglevel(Loglevel.DEBUG)
            tmc.set_direction_reg(False)
            tmc.set_current(300)
            tmc.set_interpolation(True)
            tmc.set_spreadcycle(False)
            tmc.set_microstepping_resolution(2)
            tmc.set_internal_rsense(False)
            tmc.set_motor_enabled(True)

        self.move_to_chess_origin()

    def move_to_chess_origin(self):
        
        # Find the physical origin
        self.set_speed_acceleration(loaded=True)
        self.tmc1.take_me_home(speed=self.loaded_speed, threshold=self.stallguard_threshold)

        # Move to chess origin
        self.move_in_direction(0.5, "XRIGHT")

    def move_in_direction(self, inc, direction: str):
        
        if direction in self.MOTOR_DIREC:
            bits = self.MOTOR_DIREC[direction]
            if direction in ["XLEFT", "XRIGHT", "YUP", "YDOWN"]: 
                base_step = SQUARE_STEP*inc
            elif direction in ["DUPL", "DUPR", "DDOWNL", "DDOWNR"]:
                base_step = DIAG_STEP*inc

            if bits[aPower]:
                steps = base_step * bits[aDir]
                self.tmc1.run_to_position_steps_threaded(steps, MovementAbsRel.RELATIVE)
            if bits[bPower]:
                steps = base_step * bits[bDir]
                self.tmc2.run_to_position_steps_threaded(steps, MovementAbsRel.RELATIVE)

            self.tmc1.wait_for_movement_finished_threaded()
            #self.tmc2.wait_for_movement_finished_threaded()

    def move_knight(self, delta_x, delta_y):
        if abs(delta_x) == 2 and abs(delta_y) == 1:
            self.move_in_direction(0.5, 'YUP' if delta_y > 0 else 'YDOWN')
            self.move_in_direction(2, 'XRIGHT' if delta_x > 0 else 'XLEFT')
            self.move_in_direction(0.5, 'YUP' if delta_y > 0 else 'YDOWN')
        elif abs(delta_x) == 1 and abs(delta_y) == 2:
            self.move_in_direction(0.5, 'XRIGHT' if delta_x > 0 else 'XLEFT')
            self.move_in_direction(2, 'YUP' if delta_y > 0 else 'YDOWN')
            self.move_in_direction(0.5, 'XRIGHT' if delta_x > 0 else 'XLEFT')

    def is_knight_move(self, delta_x, delta_y):
        return (abs(delta_x) == 2 and abs(delta_y) == 1) or (abs(delta_x) == 1 and abs(delta_y) == 2)

    def calculate_movement(self, move: Move):
        # Calculate differences in x and y coordinates
        delta_x = move.endX - move.startX
        delta_y = move.endY - move.startY

        print(f"DeltaX: {delta_x}, DeltaY: {delta_y}")
        if self.is_knight_move(delta_x, delta_y):
            self.move_knight(delta_x, delta_y)
        elif delta_x == delta_y:
            if delta_x > 0:
                self.move_in_direction(delta_x, "DUPR")
            else:
                self.move_in_direction(-delta_x, "DDOWNL")
        elif delta_x == -delta_y:
            if delta_x > 0:
                self.move_in_direction(delta_x, "DUPL")
            else:
                self.move_in_direction(-delta_x, "DDOWNR")
        else:
            if delta_x > 0:
                self.move_in_direction(delta_x, "XRIGHT")
            elif delta_x < 0:
                self.move_in_direction(-delta_x, "XLEFT")

            if delta_y > 0:
                self.move_in_direction(delta_y, "YUP")
            elif delta_y < 0:
                self.move_in_direction(-delta_y, "YDOWN")

    def chess_to_cartesian(self, chess_position):
        # Ensure the input string is in the correct format (e.g., "a1" to "h8")
        if len(chess_position) != 4:
            raise ValueError(f"Invalid chess position format: {chess_position}")
        if not ('a' <= chess_position[0] <= 'h') or not ('1' <= chess_position[1] <= '8'):
            raise ValueError(f"Invalid chess position format: {chess_position}")
        if not ('a' <= chess_position[2] <= 'h') or not ('1' <= chess_position[3] <= '8'):
            raise ValueError(f"Invalid chess position format: {chess_position}")

        # Convert the letter part of the chess notation to x coordinate
        startX = ord(chess_position[0]) - ord('a')
        endX = ord(chess_position[2]) - ord('a')
        # Convert the numeric part of the chess notation to y coordinate
        startY = int(chess_position[1]) - 1
        endY = int(chess_position[3]) - 1

        return self.Move(startX, startY, endX, endY)

    def make_move(self, move_string):
        move = self.chess_to_cartesian(move_string)

        # Bring the trolley to the piece
        free_move = self.Move(self.currentX, self.currentY, move.startX, move.startY)
        self.set_speed_acceleration(loaded=False)
        self.calculate_movement(free_move)

        # Make a move with that piece
        self.set_speed_acceleration(loaded=True)
        self.magnet_ON()
        self.calculate_movement(move)
        time.sleep(1)
        self.magnet_OFF()

        self.currentX = move.endX
        self.currentY = move.endY


    def demo_test(self):
        # Prompt the user for a direction
        while(True):
            position = input("Enter move: ")
            # move = self.chess_to_cartesian(position)
            # self.calculate_movement(move)
            self.make_move(position)

    def set_speed_acceleration(self, loaded):
        for tmc in [self.tmc1, self.tmc2]:    
            if loaded:        
                tmc.set_acceleration(self.loaded_acceleration)
                tmc.set_max_speed(self.loaded_speed)
            else:
                tmc.set_acceleration(self.free_acceleration)
                tmc.set_max_speed(self.free_speed)

    def magnet_ON(self):
        GPIO.output(MAGNET_PIN, GPIO.HIGH)

    def magnet_OFF(self):
        GPIO.output(MAGNET_PIN, GPIO.LOW)

    def __del__(self):
        GPIO.cleanup(MAGNET_PIN)


