import cv2
import numpy as np
import json
import os
import subprocess

# Global variables
board_state = None
IMAGE = 'images/board.jpg'
CURDIR = os.getcwd()
OUTPUT_FILE = os.path.join(CURDIR, IMAGE)
points_file = 'points.json'

def capture_image():
    command = ["rpicam-jpeg", "--timeout", "10", "--output", OUTPUT_FILE]
    try:
        subprocess.call(command)
    except Exception as e:
        print(f"An error occurred: {e}")
    # Load the image
    image_raw = cv2.imread(IMAGE)
    assert image_raw is not None, "Image not found"
    scale_percent = 30  # percent of original size
    width = int(image_raw.shape[1] * scale_percent / 100)
    height = int(image_raw.shape[0] * scale_percent / 100)
    dim = (width, height)

    # resize image
    img = cv2.resize(image_raw, dim, interpolation=cv2.INTER_AREA)
    return img

def square_occupancy_init():
    global board_state
    board_state = [
        [2, 2, 2, 2, 2, 2, 2, 2],
        [2, 2, 2, 2, 2, 2, 2, 2],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1] 
    ]

def load_squares():
    with open(points_file, 'r') as file:
        json_data = file.read()
    points = json.loads(json_data)
    row = col = 9
    return find_squares(points, row, col)

def sort_points(points):
    """Sort points by their x and y coordinates to form a grid."""
    points = sorted(points, key=lambda point: (point[0], point[1]))
    return points

def find_squares(points, row_count, col_count):
    """Find squares formed by the points in a grid."""
    squares = []
    for i in range(col_count - 1):
        for j in range(row_count - 1):
            top_left = points[i + j * row_count]
            top_right = points[(i + 1) + j * row_count]
            bottom_left = points[i + (j + 1) * row_count]
            bottom_right = points[(i + 1) + (j + 1) * row_count]
            squares.append((top_left, top_right, bottom_left, bottom_right))
    return squares

def get_combined_mask(image):
    # Convert the image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define color range for black pieces (these ranges might need adjustment)
    lower_black = np.array([90, 30, 15])
    upper_black = np.array([115, 100, 80])

    # Define color range for white pieces (these ranges might need adjustment)
    lower_white = np.array([30, 15, 145])
    upper_white = np.array([90, 80, 230])

    # Create masks for black and white pieces
    mask_black = cv2.inRange(hsv, lower_black, upper_black)
    mask_white = cv2.inRange(hsv, lower_white, upper_white)

    return mask_white, mask_black

def is_point_in_square(point, square):
    x, y = point
    top_left, top_right, bottom_left, _ = square
    return top_left[0] <= x <= top_right[0] and top_left[1] <= y <= bottom_left[1]

def detect_square_occupation(image, mask_white, mask_black, squares):
    global board_state
    contours_white, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_black, _ = cv2.findContours(mask_black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_width = 10
    min_height = 10
    game_state = [[0 for _ in range(8)] for _ in range(8)]

    # Iterate through each square
    for idx, square in enumerate(squares):
        row = 7 - (idx // 8)  # Calculate row index (0 to 7)
        col = idx % 8   # Calculate column index (0 to 7)

        square_occupied = 0  # 0 for empty, 1 for white, 2 for black
        #check for white pieces
        for contour in contours_white:
            x, y, w, h = cv2.boundingRect(contour)
            if w >= min_width and h >= min_height:
                bottom_left_corner = (x, y + h)
                bottom_right_corner = (x + w, y + h)

                if is_point_in_square(bottom_left_corner, square) or is_point_in_square(bottom_right_corner, square):
                    square_occupied = 1 # White piece
                    break
         # Copy black pieces from the previous board state to the game state
        if board_state[row][col] == 2:
            square_occupied = 2

        game_state[row][col] = square_occupied

    return game_state

def compare_board_state(previous_state, current_state):
    differences = []
    for row in range(8):
        for col in range(8):
            if previous_state[row][col] != current_state[row][col]:
                differences.append((row, col, previous_state[row][col], current_state[row][col]))
    return differences

def find_piece_movement(previous_state, current_state):

    differences = compare_board_state(previous_state, current_state)
    print(f"The length of differences: {len(differences)}")
    print(f"Moves registered: {differences}")
    # For piece movement or piece capture
    if len(differences) == 2:
        start_pos = None
        end_pos = None
        start_piece = None
        end_piece = None

        for diff in differences:
            row, col, prev_value, curr_value = diff
            if prev_value != curr_value:
                if prev_value != 0 and curr_value == 0:
                    start_pos = (row, col)
                    start_piece = prev_value
                    print(f"Start position: {(row, col)}")
                else:
                    end_pos = (row, col)
                    end_piece = curr_value
                    print(f"End position: {(row, col)}")

        if start_pos and end_pos:
            # Convert row, col indices to chess notation
            start_notation = chr(start_pos[1] + ord('a')) + str(8 - start_pos[0])
            end_notation = chr(end_pos[1] + ord('a')) + str(8 - end_pos[0])
            move = start_notation + end_notation

            # Print the piece type
            piece_type = "White" if start_piece == 1 else "Black"
            print(f"Detected move: {move} (Piece: {piece_type})")

            return move, current_state

    # Castling detection
    elif len(differences) == 4:
        king_start_pos = (7, 4)
        kingside_rook_start_pos = (7, 7)
        queenside_rook_start_pos = (7, 0)
        start_positions = [(row, col) for row, col, prev_value, curr_value in differences if prev_value == 1 and curr_value == 0]
        end_positions = [(row, col) for row, col, prev_value, curr_value in differences if prev_value == 0 and curr_value == 1]

        if king_start_pos in start_positions and any(rook_start_pos in start_positions for rook_start_pos in [kingside_rook_start_pos, queenside_rook_start_pos]):
            if (7, 6) in end_positions and (7, 5) in end_positions:  # Kingside castling
                move = 'e1g1'
                return move, current_state
            elif (7, 2) in end_positions and (7, 3) in end_positions:  # Queenside castling
                move = 'e1c1'
                return move, current_state

    print("Error: Unable to detect a valid move.")
    return None

def get_user_move():
    global board_state
    # Capture and process the current chessboard image
    chessboard_image = capture_image()
    
    mask_white, mask_black = get_combined_mask(chessboard_image)

    # Load squares
    squares = load_squares()

    # Detect current square occupation
    new_board_state = detect_square_occupation(chessboard_image, mask_white, mask_black, squares)
    for row in new_board_state:
        print(row)
    cv2.imshow('Chessboard image', chessboard_image)
    cv2.imshow('White Mask', mask_white)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    if new_board_state is None:
        print("Error: Unable to detect board state.")
    else:
        move, new_board_state = find_piece_movement(board_state, new_board_state)

        if move or board_state is None: 
            print("Error: Unable to detect a valid move.")
        else:
            board_state = new_board_state
            for row in board_state:
                print(row)


if __name__ == "__main__":
    square_occupancy_init()
    while(input("Enter any key to continue or q to exit ") != 'q'):
        get_user_move()
