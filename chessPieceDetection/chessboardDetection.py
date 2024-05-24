import cv2
import numpy as np

def invert_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    kernel = np.ones((3))
    img_dilated = cv2.dilate(edges, kernel, iterations=1)

    # Filter out all numbers and noise to isolate only boxes
    countours, _ = cv2.findContours(img_dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    countours = countours[0] if len(countours) == 2 else countours[1]
    for c in countours:
        area = cv2.contourArea(c)
        if area < 1000:
            cv2.drawContours(img_dilated, [c], -1, (0,0,0), 3)

    cv2.imshow("Image with Contours", image)
    cv2.imshow("Dilated Image with Contours", img_dilated)
    cv2.waitKey(0)

    # Fix horizontal and vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,5))
    img_dilated = cv2.morphologyEx(img_dilated, cv2.MORPH_CLOSE, vertical_kernel, iterations=9)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,1))
    img_dilated = cv2.morphologyEx(img_dilated, cv2.MORPH_CLOSE, horizontal_kernel, iterations=4)

    # Sort by top to bottom and each row by left to right
    invert = 255 - img_dilated

    cv2.imshow('invert', invert)
    cv2.waitKey(0)
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

def detect_pieces(squares):
    square_size = image.shape[1] // 8
    for i, row in enumerate(squares):
        for j, square in enumerate(row):
            white_pixels = np.sum(square == 255)
            black_pixels = np.sum(square == 0)
            text = f"{i},{j}" + (" (piece)" if black_pixels > 1500 else " (empty)")
            cx = j * square_size + square_size // 2
            cy = i * square_size + square_size // 2
            cv2.putText(image, text, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, cv2.LINE_AA)


image = cv2.imread('secondGameState.jpg')
image = cv2.resize(image, (800, 800))

invert = invert_image(image)
squares = divide_board_into_squares(invert)
detect_pieces(squares)

cv2.imshow("Original Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()