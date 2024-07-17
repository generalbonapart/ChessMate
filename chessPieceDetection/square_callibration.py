import cv2
import numpy as np
import json

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

intersection_points = open('points.json')
sorted_points = sort_points(intersection_points)
# squares = find_squares(sorted_points, 9, 9)

print(sorted_points)
