import cv2
import numpy as np

def get_board_corners(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    kernel = np.ones((3))
    img_dilated = cv2.dilate(edges, kernel, iterations=1)
    contours, _ = cv2.findContours(img_dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.imshow("Image", img_dilated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # cnts = contours[0] if len(contours) == 2 else contours[1]
    # for cnt in cnts:
    #     approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
    #     print(len(approx))
    #     if len(approx) == 4:
    #         print("Red = square")
    #         cv2.drawContours(image, [cnt], -1, (0, 255, 0), 3)

    # Ensure contours are found
    if not contours:
        raise ValueError("No contours found in the image.")
    
    board_contour = max(contours, key=cv2.contourArea)
    epsilon = 0.1 * cv2.arcLength(board_contour, True)
    corners = cv2.approxPolyDP(board_contour, epsilon, True)
    
    # Ensure exactly 4 corners are found
    # if len(corners) != 4:
    #     raise ValueError(f"Expected 4 corners, but found {len(corners)}.")
    
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

def detect_pieces(square_image):
    gray = cv2.cvtColor(square_image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    kernel = np.ones((3))
    img_dilated = cv2.dilate(edges, kernel, iterations=1)
    contours, _ = cv2.findContours(img_dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    print(len(contours))
    # cv2.imshow("Image", img_dilated)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return len(contours) > 2 # Return True if any contours are found, indicating a piece

image = cv2.imread('chessboard_simple.jpg')
image = cv2.resize(image, (800, 800))

square_size = image.shape[1] // 8

get_board_corners(image)
squares = divide_board_into_squares(image)
# for i, row in enumerate(squares):
#     for j, square in enumerate(row):
#         cv2.imshow(f"Square {i},{j}", square)
#         cv2.waitKey(100)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# Check for pieces in each square and annotate the original image
for i, row in enumerate(squares):
    for j, square in enumerate(row):
        occupied = detect_pieces(square)
        text = f"{i},{j}" + (" (piece)" if occupied else " (empty)")
        cx = j * square_size + square_size // 2
        cy = i * square_size + square_size // 2
        cv2.putText(image, text, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, cv2.LINE_AA)

cv2.imshow("Original Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()