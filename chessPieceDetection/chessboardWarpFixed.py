import cv2 as cv
import numpy as np

img = cv.imread('chessboard_unwarped.jpg')
img = cv.resize(img, (1000, 1000))

assert img is not None, "file could not be read, check with os.path.exists()"
rows,cols,ch = img.shape
pts1 = np.float32([[124, 150],[835,150],[150, 920],[935,920]])
pts2 = np.float32([[0,0],[500,0],[0,500],[500,500]])
M = cv.getPerspectiveTransform(pts1,pts2)
dst = cv.warpPerspective(img,M,(500,500))


# Display the input and output images
cv.imshow('Input', img)
cv.imshow('Output', dst)
cv.waitKey(0)
cv.destroyAllWindows()