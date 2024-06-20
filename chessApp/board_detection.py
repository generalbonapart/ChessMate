import cv2
import numpy as np
import os
import subprocess

board_state = None
IMAGE = 'images/board.jpg'
CURDIR = os.getcwd()
OUTPUT_FILE = os.path.join(CURDIR, IMAGE)

def print_board_state():
    print("\n")
    for row in board_state:
        print(" ".join(piece if piece is not None else '.' for piece in row))
    print("\n")

def initialize_board(color):
    if color == 'white':
        return [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]

def divide_board_into_squares(board_image, grid_size=8):
    height, width = board_image.shape[:2]
    square_size = width // grid_size
    squares = []
    for y in range(0, height, square_size):
        row = []
        for x in range(0, width, square_size):
            square = board_image[y:y + square_size, x:x + square_size]
            row.append(square)
        squares.append(row)
    return squares

def detect_pieces(squares, board_state):
    new_board_state = [row[:] for row in board_state]

    for i, row in enumerate(squares):
        for j, square in enumerate(row):
            white_pixels = np.sum(square == 255)
            if white_pixels > 500:
                if new_board_state [i][j] in ['p', 'r', 'n', 'b', 'q', 'k', 'P', 'R', 'N', 'B', 'Q', 'K']:
                    continue
                else:
                    new_board_state [i][j] = 'm'  # Denoted new move with m
            else:
                new_board_state [i][j] = None
    return new_board_state 

def detect_move(previous_board, current_board):
    start_pos = None
    end_pos = None
    moved_piece = None

    for i in range(8):
        for j in range(8):
            if previous_board[i][j] != current_board[i][j]:
                if current_board[i][j] == 'm':
                    end_pos = (i, j)
                if previous_board[i][j] is not None:
                    start_pos = (i, j)
                    moved_piece = previous_board[start_pos[0]][start_pos[1]]

    if start_pos and end_pos:
        current_board[end_pos[0]][end_pos[1]] = moved_piece
        current_board[start_pos[0]][start_pos[1]] = None
        start = chr(start_pos[1] + ord('a')) + str(8 - start_pos[0])
        end = chr(end_pos[1] + ord('a')) + str(8 - end_pos[0])
        return start + end, current_board
    return None, current_board

# Generate a combined mask for detecting black and white pieces
def get_combined_mask(image):
    # Convert the image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define color range for black pieces (these ranges might need adjustment)
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 50])

    # Define color range for white pieces (these ranges might need adjustment)
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 55, 255])

    # Create masks for black and white pieces
    mask_black = cv2.inRange(hsv, lower_black, upper_black)
    mask_white = cv2.inRange(hsv, lower_white, upper_white)

    # Combine masks
    combined_mask = cv2.bitwise_or(mask_black, mask_white)
    
    return combined_mask

def report_bot_move(move):
    start = move[0:2]
    end = move[2:]
    start_pos = (8 - int(start[1]), ord(start[0]) - ord('a'))
    end_pos = (8 - int(end[1]), ord(end[0]) - ord('a'))
    moved_piece = board_state[start_pos[0]][start_pos[1]]
    board_state[end_pos[0]][end_pos[1]] = moved_piece
    board_state[start_pos[0]][start_pos[1]] = None
    print_board_state()
    
def board_detection_init():
    global board_state
    board_state = initialize_board('white')

def get_user_move():
    
    global board_state

    command = ["rpicam-jpeg", "--timeout", "10", "--output", OUTPUT_FILE]
    try:
        subprocess.call(command)
    except Exception as e:
        print(f"An error occurred: {e}")
    # Load the image
    image_raw = cv2.imread(IMAGE)
    assert image_raw is not None, "Image not found"
    image_raw = cv2.resize(image_raw, (800, 800))

    pts1 = np.float32([[130, 88],[657, 17],[70, 799],[799,774]])
    pts2 = np.float32([[0,0],[800,0],[0,800],[800,800]])
    M = cv2.getPerspectiveTransform(pts1,pts2)
    dst = cv2.warpPerspective(image_raw,M,(800,800))
    image = cv2.rotate(dst, cv2.ROTATE_90_CLOCKWISE)

    # Detect move
    combined_mask = get_combined_mask(image)
    squares = divide_board_into_squares(combined_mask)
    new_board_state = detect_pieces(squares, board_state)
    move, board_state = detect_move(board_state, new_board_state)
    return move