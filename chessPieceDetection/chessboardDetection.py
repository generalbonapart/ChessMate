import cv2
import numpy as np

def initialize_board():
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

def print_board_state(board_state):
    for row in board_state:
        print(" ".join(piece if piece is not None else '.' for piece in row))

def is_circle_like(contour, circularity_threshold=0.8):
    """ Determine if a contour is circle-like based on its circularity. """
    perimeter = cv2.arcLength(contour, True)
    area = cv2.contourArea(contour)
    if perimeter == 0 or area == 0:
        return False
    circularity = 4 * np.pi * (area / (perimeter ** 2))
    return circularity > circularity_threshold

def is_curved(contour, threshold=0.05):
    perimeter = cv2.arcLength(contour, True)
    area = cv2.contourArea(contour)
    if area == 0:
        return False
    ratio = perimeter**2 / (4 * np.pi * area)
    return ratio > threshold

def invert_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    kernel = np.ones((3))
    img_dilated = cv2.dilate(edges, kernel, iterations=1)

    contours, _ = cv2.findContours(img_dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.ones_like(gray) * 255  # White background
    # Fill curved contours with black
    for cnt in contours:
        if is_curved(cnt):
            cv2.fillPoly(mask, [cnt], 0)

    cv2.imshow('inverted', mask)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Filter out all numbers and noise to isolate only boxes
    contours, _ = cv2.findContours(img_dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    for c in contours:
        cv2.drawContours(img_dilated, [c], -1, (0,0,0), thickness=cv2.FILLED)
    '''
    for c in countours:
        area = cv2.contourArea(c)
        if area < 1000:
            cv2.drawContours(img_dilated, [c], -1, (0,0,0), thickness=cv2.FILLED)

    # Fix horizontal and vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,5))
    img_dilated = cv2.morphologyEx(img_dilated, cv2.MORPH_CLOSE, vertical_kernel, iterations=10)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,1))
    img_dilated = cv2.morphologyEx(img_dilated, cv2.MORPH_CLOSE, horizontal_kernel, iterations=10)
    '''

    # Sort by top to bottom and each row by left to right
    invert = 255 - img_dilated
 
    return invert
    
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
            black_pixels = np.sum(square == 0)
            if black_pixels > 1500:
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
                    moved_piece = previous_board[start_pos[0]][end_pos[1]]

    if start_pos and end_pos:
        current_board[end_pos[0]][end_pos[1]] = moved_piece
        current_board[start_pos[0]][start_pos[1]] = None
        start = chr(start_pos[1] + ord('a')) + str(8 - start_pos[0])
        end = chr(end_pos[1] + ord('a')) + str(8 - end_pos[0])
        return start + end, current_board
    return None, current_board

image = cv2.imread('output.jpg')
image = cv2.resize(image, (800, 800))
board_state = initialize_board()
invert = invert_image(image)
squares = divide_board_into_squares(invert)
new_board_state = detect_pieces(squares, board_state)
print_board_state(new_board_state)
move, updated_board_state = detect_move(board_state, new_board_state)
print_board_state(updated_board_state)
print(move)
