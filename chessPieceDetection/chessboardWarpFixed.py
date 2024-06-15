import cv2 as cv
import numpy as np

img = cv.imread('test.jpg')
img = cv.resize(img, (800, 800))

assert img is not None, "file could not be read, check with os.path.exists()"
rows,cols,ch = img.shape
pts1 = np.float32([[149, 84],[653, 11],[27,770],[793,769]])
pts2 = np.float32([[0,0],[800,0],[0,800],[800,800]])
M = cv.getPerspectiveTransform(pts1,pts2)
dst = cv.warpPerspective(img,M,(800,800))

rotated_image = cv.rotate(dst, cv.ROTATE_90_CLOCKWISE)

cv.imwrite('output.jpg', rotated_image)

# Display the input and output images
cv.imshow('Input', img)
cv.imshow('Output', rotated_image)
cv.waitKey(0)
cv.destroyAllWindows()
