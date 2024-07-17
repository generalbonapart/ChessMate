import cv2
import numpy as np
import json

# Global variable to store points
points = []

# Mouse callback function to capture click events
def click_event(event, x, y, flags, params):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        # Draw a circle at the clicked point
        cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow('image', image)

# Load the image
image = cv2.imread('images/empty_board.jpg')

scale_percent = 20 # percent of original size
width = int(image.shape[1] * scale_percent / 100)
height = int(image.shape[0] * scale_percent / 100)
dim = (width, height)
  
# resize image
img = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
pts1 = np.float32([[279,130],[636,138],[8,517],[894,516]])
pts2 = np.float32([[0,0],[800,0],[0,800],[800,800]])
M = cv2.getPerspectiveTransform(pts1,pts2)
image = cv2.warpPerspective(img,M,(800,800))

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