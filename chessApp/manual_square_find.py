import cv2
import numpy as np
import json
import os
import subprocess

# Global variable to store points
points = []

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
    scale_percent = 20  # percent of original size
    width = int(image_raw.shape[1] * scale_percent / 100)
    height = int(image_raw.shape[0] * scale_percent / 100)
    dim = (width, height)

    # resize image
    img = cv2.resize(image_raw, dim, interpolation=cv2.INTER_AREA)
    pts1 = np.float32([[279, 130], [636, 138], [8, 517], [894, 516]])
    pts2 = np.float32([[0, 0], [800, 0], [0, 800], [800, 800]])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    return cv2.warpPerspective(img, M, (800, 800))

# Mouse callback function to capture click events
def click_event(event, x, y, flags, params):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        # Draw a circle at the clicked point
        cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow('image', image)

# Load the image
image = capture_image()

cv2.imshow('image', image)

# Set the mouse callback function
cv2.setMouseCallback('image', click_event)

# Wait until 'q' key is pressed to break the loop
while True:
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

# Save the points to a JSON file
with open('points.json', 'w') as f:
    json.dump(points, f)

print(f"Points saved: {points}")

cv2.destroyAllWindows()