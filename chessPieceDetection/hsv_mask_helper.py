import cv2
import numpy as np

# Load the image
image = cv2.imread('images/board.jpg')
assert image is not None, "file could not be read, check with os.path.exists()"

scale_percent = 30  # percent of original size
width = int(image.shape[1] * scale_percent / 100)
height = int(image.shape[0] * scale_percent / 100)
dim = (width, height)
# resize image
img = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
h, s, v = cv2.split(hsv)
# Display each channel if needed
cv2.imshow('Adjusted Hue Channel', h)
cv2.imshow('Adjusted Saturation Channel', s)
cv2.imshow('Adjusted Value Channel', v)

# Define color range for black pieces (these ranges might need adjustment)
lower_black = np.array([80, 30, 15])
upper_black = np.array([120, 100, 80])

# Define color range for white pieces (these ranges might need adjustment)
lower_white = np.array([20, 15, 145])
upper_white = np.array([100, 80, 230])

# Create masks for black and white pieces
black_mask = cv2.inRange(hsv, lower_black, upper_black)
white_mask = cv2.inRange(hsv, lower_white, upper_white)

cv2.imshow('Black mask', black_mask)
cv2.imshow('White mask', white_mask)
cv2.waitKey(0)
cv2.destroyAllWindows()
