import sys
import time
from src.TMC_2209_StepperDriver import *

# Define variables for aDir, bDir, aPower, bPower
aDir = 0
bDir = 1
aPower = 2
bPower = 3

SQUARE_STEP = 515
DIAG_STEP = 727

class Trolley:

    # Motor control settings [aDir, bDir, aPower, bPower]
    MOTOR_DIREC = {
        "XRIGHT": [1, 1, 1, 1],
        "XLEFT": [-1, -1, 1, 1],
        "YUP": [1, -1, 1, 1],
        "YDOWN": [-1, 1, 1, 1],
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

    def __init__(self, speed = 1000):

        self.tmc1 = TMC_2209(21, 16, 20, driver_address=0)
        self.tmc2 = TMC_2209(26, 13, 19, driver_address=1)
        self.speed = speed
        for tmc in [self.tmc1, self.tmc2]:

            tmc.tmc_logger.set_loglevel(Loglevel.DEBUG)

            tmc.set_direction_reg(False)
            tmc.set_current(300)
            tmc.set_interpolation(True)
            tmc.set_spreadcycle(False)
            tmc.set_microstepping_resolution(2)
            tmc.set_internal_rsense(False)
            tmc.set_acceleration(1000)
            tmc.set_max_speed(self.speed)
            tmc.set_motor_enabled(True)

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
            self.tmc2.wait_for_movement_finished_threaded()

    def calculate_movement(self, move: Move):
        # Calculate differences in x and y coordinates
        delta_x = move.endX - move.startX
        delta_y = move.endY - move.startY

        print(f"DeltaX: {delta_x}, DeltaY: {delta_y}")

        if delta_x == delta_y:
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


    def demo_test(self):
        # Prompt the user for a direction
        while(True):
            position = input("Enter move: ")
            move = self.chess_to_cartesian(position)
            self.calculate_movement(move)

trolley = Trolley(1000)
trolley.demo_test()



