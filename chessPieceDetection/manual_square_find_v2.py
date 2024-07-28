import cv2
import numpy as np
import json
import os
import subprocess
from square_occupancy_v2 import capture_image

# Global variable to store points
points = []

# Global variables
board_state = None
IMAGE = 'images/board.jpg'
CURDIR = os.getcwd()
OUTPUT_FILE = os.path.join(CURDIR, IMAGE)
points_file = 'points.json'

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
if len(points) == 81: 
    with open('points.json', 'w') as f:
        json.dump(points, f)

    print(f"Points saved: {points}")

else:
    print(f"Incorrect number of points clicked: {len(points)}")

cv2.destroyAllWindows()
