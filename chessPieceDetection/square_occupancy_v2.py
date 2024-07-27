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
    scale_percent = 50  # percent of original size
    width = int(image_raw.shape[1] * scale_percent / 100)
    height = int(image_raw.shape[0] * scale_percent / 100)
    dim = (width, height)

    # resize image
    img = cv2.resize(image_raw, dim, interpolation=cv2.INTER_AREA)
    pts1 = np.float32([[505, 65],[1608, 18],[592, 1228],[1707, 1097]])
    pts2 = np.float32([[0,0],[800,0],[0,800],[800,800]])
    M = cv2.getPerspectiveTransform(pts1,pts2)
    return cv2.warpPerspective(img,M,(800,800))

def square_occupancy_init():
    global board_state
    board_state = [
        [1, 1, 1, 1, 1, 1, 1, 1],  # 8th rank (Black's major pieces)
        [1, 1, 1, 1, 1, 1, 1, 1],  # 7th rank (Black's pawns)
        [0, 0, 0, 0, 0, 0, 0, 0],  # 6th rank (empty squares)
        [0, 0, 0, 0, 0, 0, 0, 0],  # 5th rank (empty squares)
        [0, 0, 0, 0, 0, 0, 0, 0],  # 4th rank (empty squares)
        [0, 0, 0, 0, 0, 0, 0, 0],  # 3rd rank (empty squares)
        [1, 1, 1, 1, 1, 1, 1, 1],  # 2nd rank (White's pawns)
        [1, 1, 1, 1, 1, 1, 1, 1]   # 1st rank (White's major pieces)
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
    lower_black = np.array([95, 30, 15])
    upper_black = np.array([115, 100, 80])

    # Define color range for white pieces (these ranges might need adjustment)
    lower_white = np.array([30, 15, 145])
    upper_white = np.array([80, 80, 230])

    # Create masks for black and white pieces
    mask_black = cv2.inRange(hsv, lower_black, upper_black)
    mask_white = cv2.inRange(hsv, lower_white, upper_white)

    # Combine masks
    combined_mask = cv2.bitwise_or(mask_black, mask_white)

    return white_mask, black_mask

def is_point_in_square(point, square):
    x, y = point
    top_left, top_right, bottom_left, _ = square
    return top_left[0] <= x <= top_right[0] and top_left[1] <= y <= bottom_left[1]

def detect_square_occupation(image, binary_mask, squares):
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_width = 12
    min_height = 12
    
    game_state = [[0 for _ in range(8)] for _ in range(8)]

    # Iterate through each square
    for idx, square in enumerate(squares):
        row = idx // 8  # Calculate row index (0 to 7)
        col = idx % 8   # Calculate column index (0 to 7)

        square_occupied = False
        # Iterate through each contour
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w >= min_width and h >= min_height:
                bottom_left_corner = (x, y + h)
                bottom_right_corner = (x + w, y + h)

                if is_point_in_square(bottom_left_corner, square) or is_point_in_square(bottom_right_corner, square):
                    square_occupied = True
                    break

        game_state[row][col] = 1 if square_occupied else 0

        # Draw the square on the output image
        color = (0, 255, 0) if square_occupied else (0, 0, 255)
        top_left, top_right, bottom_left, bottom_right = square
        cv2.rectangle(image, tuple(top_left), tuple(bottom_right), color, 2)
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
    
    if len(differences) == 2:
        start_pos = None
        end_pos = None
        for diff in differences:
            row, col, prev_value, curr_value = diff
            if prev_value == 1 and curr_value == 0:
                start_pos = (row, col)
            elif prev_value == 0 and curr_value == 1:
                end_pos = (row, col)

        if start_pos and end_pos:
            # Normal move
            start_notation = chr(start_pos[1] + ord('a')) + str(start_pos[0] + 1)
            end_notation = chr(end_pos[1] + ord('a')) + str(end_pos[0] + 1)
            move = start_notation + end_notation
            return move, current_state

    elif len(differences) == 1:
        diff = differences[0]
        row, col, prev_value, curr_value = diff
        if prev_value == 0 and curr_value == 1:
            end_pos = (row, col)
            # Assume the start position is the square that was previously occupied
            start_pos = find_start_pos(previous_state, end_pos)

            if start_pos:
                # Capture move
                start_notation = chr(start_pos[1] + ord('a')) + str(start_pos[0] + 1)
                end_notation = chr(end_pos[1] + ord('a')) + str(end_pos[0] + 1)
                move = start_notation + end_notation
                return move, current_state

    print("Error: Unable to detect a valid move.")
    return None

def get_user_move():
    global board_state
    # Capture and process the current chessboard image
    chessboard_image = capture_image()
    
    combined_mask = get_combined_mask(chessboard_image)

    # Load squares
    squares = load_squares()

    # Detect current square occupation
    new_board_state = detect_square_occupation(chessboard_image, combined_mask, squares)
    for row in new_board_state:
        print(row)
    differences = compare_board_state(board_state, new_board_state)
    print(differences)
    #move, board_state = find_piece_movement(board_state, new_board_state)
    #print(move)
    cv2.imshow('Chessboard image', chessboard_image)
    cv2.imshow('Combined image', combined_mask)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    square_occupancy_init()
    while(input("Enter any key to continue or q to exit ") != 'q'):
        get_user_move()
