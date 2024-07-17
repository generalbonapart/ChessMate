import cv2
import numpy as np
import json

# TODO: Change this to use RPI-CAM command in the future
def capture_image():
    image = cv2.imread('images/board_6.jpg')
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

# Colour Thresholding detection method
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

# Contour Detection method
def detect_contours(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def check_square_occupancy(image, filtered_image, squares):
    gray = cv2.cvtColor(filtered_image, cv2.COLOR_BGR2GRAY)

    for idx, square in enumerate(squares):
        top_left, top_right, bottom_left, bottom_right = square

        # Create a mask for the square
        mask = np.zeros_like(gray)
        roi_corners = np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.int32)
        cv2.fillPoly(mask, [roi_corners], (255, 255, 255))

        # Apply the mask to the grayscale image
        square_image = cv2.bitwise_and(gray, mask)

        kernel = np.ones((5, 5), np.uint8)
        closed_image = cv2.morphologyEx(square_image, cv2.MORPH_CLOSE, kernel)

        # # Calculate the mean intensity to determine occupancy
        # mean_intensity = np.mean(square_image)

        # print(f"Square idx: {idx} Mean Intensity: {mean_intensity}")

        # # Determine if the square is occupied based on mean intensity threshold
        # occupied = mean_intensity > 2  # Adjust threshold as needed

         # Calculate gradients using Sobel operator
        grad_x = cv2.Sobel(square_image, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(square_image, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = cv2.magnitude(grad_x, grad_y)

        # Threshold the gradient image to get binary edges
        # _, binary_edges = cv2.threshold(gradient_magnitude, 100, 255, cv2.THRESH_BINARY)
        binary_edges = cv2.adaptiveThreshold(closed_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        blur = cv2.GaussianBlur(square_image,(5,5),0)
        ret3,th3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        # Find contours in the binary edges image
        # contours, _ = cv2.findContours(binary_edges.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours, _ = cv2.findContours(th3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        print(f'Square {idx} Countours {len(contours)}')

        # Determine if the square is occupied based on the number and size of contours
        occupied = len(contours) >= 1

        cv2.drawContours(square_image, contours, -1, (255, 255, 255), 1)

        # Draw rectangle on the original image based on occupancy
        color = (0, 255, 0) if occupied else (0, 0, 255)
        cv2.rectangle(image, top_left, bottom_right, color, thickness=2)

        text = "Occupied" if occupied else "Empty"
        text_position = (top_left[0] + 5, top_left[1] + 20)  # Adjust the offset as needed
        cv2.putText(image, text + str(idx), text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
        
        cv2.imshow(f'Square {idx}', square_image)

    return image

def get_combined_mask(image):
    # Convert the image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define color range for black pieces (these ranges might need adjustment)
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([50, 50, 50])

    # Define color range for white pieces (these ranges might need adjustment)
    lower_white = np.array([60, 45, 160])
    upper_white = np.array([100, 90, 180])

    # Create masks for black and white pieces
    mask_black = cv2.inRange(hsv, lower_black, upper_black)
    mask_white = cv2.inRange(hsv, lower_white, upper_white)

    # Combine masks
    combined_mask = cv2.bitwise_or(mask_black, mask_white)
    
    return combined_mask

if __name__ == "__main__":

    with open('points.json', 'r') as file:
        json_data = file.read()    
    points = json.loads(json_data)
    squares = find_squares(points, 9, 9)

    chessboard_image = capture_image()

    gray = cv2.cvtColor(chessboard_image, cv2.COLOR_BGR2GRAY)

    hsv = cv2.cvtColor(chessboard_image, cv2.COLOR_BGR2HSV)

    hue_threshold = 45  # Adjust this threshold value as needed
    lower_bound = np.array([hue_threshold, 0, 0])  # Hue threshold and minimum for S and V
    upper_bound = np.array([200, 255, 255])  # Maximum for S and V

    # Create a mask using the inRange function to filter out values above the hue threshold
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    filtered_image = cv2.bitwise_and(chessboard_image, chessboard_image, mask=mask)

    # Extract HSV channels
    h, s, v = cv2.split(hsv)
    # Display each channel if needed
    cv2.imshow('Adjusted Hue Channel', h)
    cv2.imshow('Adjusted Saturation Channel', s)
    cv2.imshow('Adjusted Value Channel', v)

    # Define color range for black pieces (these ranges might need adjustment)
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([110, 100, 40])

    # Define color range for white pieces (these ranges might need adjustment)
    lower_white = np.array([50, 25, 150])
    upper_white = np.array([80, 55, 220])

    # Create masks for black and white pieces
    mask_black = cv2.inRange(hsv, lower_black, upper_black)
    mask_white = cv2.inRange(hsv, lower_white, upper_white)

    # Combine masks
    combined_mask = cv2.bitwise_or(mask_black, mask_white)

    cv2.imshow('Chessboard image', chessboard_image)
    cv2.imshow('Combined image', combined_mask)
    cv2.waitKey(0)
    cv2.destroyAllWindows()