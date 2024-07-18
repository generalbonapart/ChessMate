import cv2
import numpy as np
import json

class SquareOccupancyDetector:

    def __init__(self):
        self.points_file = 'points.json'
        self.squares = self.load_squares()

    # TODO: Change this to use RPI-CAM command in the future
    def capture_image(self):
        image = cv2.imread('images/board_5.jpg')
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

    def load_squares(self):
        with open(self.points_file, 'r') as file:
            json_data = file.read()
        points = json.loads(json_data)
        row = col = 9
        return self.find_squares(points, row, col)
    
    @staticmethod
    def sort_points(points):
        """Sort points by their x and y coordinates to form a grid."""
        points = sorted(points, key=lambda point: (point[0], point[1]))
        return points
    
    @staticmethod
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

    @staticmethod
    def get_combined_mask(image):
        # Convert the image to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define color range for black pieces (these ranges might need adjustment)
        lower_black = np.array([50, 30, 0])
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
    @staticmethod
    def is_point_in_square(point, square):
        x, y = point
        top_left, top_right, bottom_left, _ = square
        return top_left[0] <= x <= top_right[0] and top_left[1] <= y <= bottom_left[1]

    def detect_square_occupation(self, image, binary_mask):
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_width = 15
        min_height = 10
        game_state = [[0 for _ in range(8)] for _ in range(8)]

        # Iterate through each square
        for idx, square in enumerate(self.squares):
            row = idx // 8  # Calculate row index (0 to 7)
            col = idx % 8   # Calculate column index (0 to 7)

            square_occupied = False
            # Iterate through each contour
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w >= min_width and h >= min_height:
                    bottom_left_corner = (x, y + h)
                    bottom_right_corner = (x + w, y + h)

                    if self.is_point_in_square(bottom_left_corner, square) or self.is_point_in_square(bottom_right_corner, square):
                        square_occupied = True
                        break

            game_state[row][col] = 1 if square_occupied else 0

            # Draw the square on the output image
            color = (0, 255, 0) if square_occupied else (0, 0, 255)
            top_left, top_right, bottom_left, bottom_right = square
            cv2.rectangle(image, tuple(top_left), tuple(bottom_right), color, 2)
        return game_state
    
    @staticmethod
    def save_board_state(file_path, board_state):
        with open(file_path, 'w') as f:
            json.dump(board_state, f)

    def process_chessboard(self):
        # Capture and process the current chessboard image
        chessboard_image = self.capture_image()

        # Get combined mask
        combined_mask = self.get_combined_mask(chessboard_image)

        # Detect current square occupation
        current_state = self.detect_square_occupation(chessboard_image, combined_mask)
        self.save_board_state('images/previous_boardstate', current_state)
        
        # Show the image with detected squares
        for row in current_state:
            print(row)
        cv2.imshow('Chessboard image', chessboard_image)
        cv2.imshow('Combined image', combined_mask)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def show_HSV(img):
        # Extract HSV channels
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        # Display each channel if needed
        cv2.imshow('Adjusted Hue Channel', h)
        cv2.imshow('Adjusted Saturation Channel', s)
        cv2.imshow('Adjusted Value Channel', v)

if __name__ == "__main__":
    detector = SquareOccupancyDetector()
    detector.process_chessboard()