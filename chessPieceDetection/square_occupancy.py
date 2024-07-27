import chessboard_callibration as chessboard

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


def check_square_occupancy(image):
    preprocessed_image = preprocess_image(image)
    occupied_squares = []

    for idx, square in enumerate(chessboard.squares_global):
        top_left, top_right, bottom_left, bottom_right = square
        square_mask = np.zeros_like(preprocessed_image)
        roi_corners = np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.int32)
        cv2.fillPoly(square_mask, [roi_corners], (255, 255, 255))
        
        square_image = cv2.bitwise_and(preprocessed_image, square_mask)

        diff_mask = color_thresholding(square_image)

        contours = detect_contours(diff_mask)

        occupied = len(contours) > 0
        if occupied:
            occupied_squares.append(idx)

        # Visualization (Optional)
        color = (0, 255, 0) if occupied else (0, 0, 255)
        cv2.rectangle(image, top_left, bottom_right, color, thickness=2)

    return image, occupied_squares

if __name__ == "__main__":

    chessboard_image = chessboard.get_chessboard()

    result_image, occupied_squares = check_square_occupancy(chessboard_image, empty_board_image)
    cv2.imshow('Result', result_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()