import cv2
import numpy as np
import json

# TODO: Change this to use RPI-CAM command in the future
def capture_image():
    image = cv2.imread('images/board_10.jpg')
    scale_percent = 20 # percent of original size
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    
    # resize image
    img = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
    pts1 = np.float32([[279,130],[636,138],[8,517],[894,516]])
    pts2 = np.float32([[0,0],[800,0],[0,800],[800,800]])
    M = cv2.getPerspectiveTransform(pts1,pts2)
    return cv2.warpPerspective(img,M,(800,800))

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
            top_right = points[(i+1) + j * row_count]
            bottom_left = points[(i) + (j + 1) * row_count]
            bottom_right = points[(i + 1) + (j + 1) * row_count]
            squares.append((top_left, top_right, bottom_left, bottom_right))
    return squares

def get_combined_mask(image):
    # Convert the image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define color range for black pieces (these ranges might need adjustment)
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([110, 100, 40])

    # Define color range for white pieces (these ranges might need adjustment)
    lower_white = np.array([36, 30, 145])
    upper_white = np.array([80, 75, 220])

    # Create masks for black and white pieces
    mask_black = cv2.inRange(hsv, lower_black, upper_black)
    mask_white = cv2.inRange(hsv, lower_white, upper_white)

    # Combine masks
    combined_mask = cv2.bitwise_or(mask_black, mask_white)

    return combined_mask

# Function to check if a point is within a square
def is_point_in_square(point, square):
    x, y = point
    top_left, top_right, bottom_left, _ = square
    return top_left[0] <= x <= top_right[0] and top_left[1] <= y <= bottom_left[1]

def detect_square_occupation(image, binary_mask):
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_width = 15
    min_height = 10
    
    # Iterate through each square
    for square in squares:
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

        # Draw the square on the output image
        color = (0, 255, 0) if square_occupied else (0, 0, 255)
        top_left, _, _, bottom_right = square
        cv2.rectangle(image, tuple(top_left), tuple(bottom_right), color, 2)


if __name__ == "__main__":

    with open('points.json', 'r') as file:
        json_data = file.read()    
    points = json.loads(json_data)
    squares = find_squares(points, 9, 9)

    chessboard_image = capture_image()

    # Extract HSV channels
    hsv = cv2.cvtColor(chessboard_image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    # Display each channel if needed
    cv2.imshow('Adjusted Hue Channel', h)
    cv2.imshow('Adjusted Saturation Channel', s)
    cv2.imshow('Adjusted Value Channel', v)

    combined_mask = get_combined_mask(chessboard_image)

    detect_square_occupation(chessboard_image, combined_mask)

    cv2.imshow('Chessboard image', chessboard_image)
    cv2.imshow('Combined image', combined_mask)
    cv2.waitKey(0)
    cv2.destroyAllWindows()