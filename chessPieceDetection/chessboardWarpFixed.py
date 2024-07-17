import cv2 as cv
import numpy as np

# Load the image
image = cv.imread('images/board1.jpg')
assert image is not None, "file could not be read, check with os.path.exists()"

scale_percent = 20 # percent of original size
width = int(image.shape[1] * scale_percent / 100)
height = int(image.shape[0] * scale_percent / 100)
dim = (width, height)
  
# resize image
image = cv.resize(image, dim, interpolation = cv.INTER_AREA)

# rows,cols,ch = image.shape
pts1 = np.float32([[328, 136],[602, 138],[177, 392],[753, 394]])
pts2 = np.float32([[0,0],[800,0],[0,800],[800,800]])
M = cv.getPerspectiveTransform(pts1,pts2)
dst = cv.warpPerspective(image,M,(800,800))

rotated_image = cv.rotate(dst, cv.ROTATE_90_CLOCKWISE)

cv.imwrite('output.jpg', rotated_image)

# Display the input and output images
cv.imshow('Input', image)
cv.imshow('Output', rotated_image)
cv.waitKey(0)
cv.destroyAllWindows()
