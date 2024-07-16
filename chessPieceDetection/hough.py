import cv2
import numpy as np
import math

def angle_between_lines(line1, line2):
    """Calculate the smallest angle between two lines."""
    rho1, theta1 = line1
    rho2, theta2 = line2
    return min(abs(theta1 - theta2), np.pi - abs(theta1 - theta2))

def distance_between_lines(line1, line2):
    """Calculate the absolute distance between two lines."""
    rho1, theta1 = line1
    rho2, theta2 = line2
    return abs(rho1 - rho2)

def cluster_lines(lines, distance_threshold, angle_threshold):
    """Cluster lines based on distance and angle thresholds."""
    clusters = []
    
    for line in lines:
        added_to_cluster = False
        for cluster in clusters:
            if (distance_between_lines(cluster[0], line) < distance_threshold and
                    angle_between_lines(cluster[0], line) < angle_threshold):
                cluster.append(line)
                added_to_cluster = True
                break
        if not added_to_cluster:
            clusters.append([line])
    
    return clusters

def merge_clusters(clusters):
    """Merge clusters by averaging the lines in each cluster."""
    merged_lines = []
    for cluster in clusters:
        if len(cluster) == 1:
            merged_lines.append(cluster[0])
        else:
            avg_rho = np.mean([line[0] for line in cluster])
            avg_theta = np.mean([line[1] for line in cluster])
            merged_lines.append((avg_rho, avg_theta))
    return merged_lines

def draw_lines(image, lines, color=(0, 0, 255), thickness=2):
    """Draw lines on an image."""
    for rho, theta in lines:
        a = math.cos(theta)
        b = math.sin(theta)
        x0 = a * rho
        y0 = b * rho
        pt1 = (int(x0 + 1000 * (-b)), int(y0 + 1000 * (a)))
        pt2 = (int(x0 - 1000 * (-b)), int(y0 - 1000 * (a)))
        cv2.line(image, pt1, pt2, color, thickness, cv2.LINE_AA)

def find_intersection(line1, line2):
    """Find the intersection of two lines given in (rho, theta) format."""
    rho1, theta1 = line1
    rho2, theta2 = line2
    A = np.array([[np.cos(theta1), np.sin(theta1)],
                  [np.cos(theta2), np.sin(theta2)]])
    b = np.array([rho1, rho2])
    if np.linalg.det(A) == 0:
        return None
    x0, y0 = np.linalg.solve(A, b)
    return (int(np.round(x0)), int(np.round(y0)))

def get_intersection_points(horizontal_lines, vertical_lines):
    intersection_points = []
    for h_line in horizontal_lines:
        for v_line in vertical_lines:
            point = find_intersection(h_line, v_line)
            if point:
                intersection_points.append(point)
    return intersection_points

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

# Load the image
image = cv2.imread('images/board.jpg')

scale_percent = 20 # percent of original size
width = int(image.shape[1] * scale_percent / 100)
height = int(image.shape[0] * scale_percent / 100)
dim = (width, height)
  
# resize image
img = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

pts1 = np.float32([[318, 140],[608, 147],[150, 425],[776, 430]])
pts2 = np.float32([[0,0],[1000,0],[0,1000],[1000,1000]])
M = cv2.getPerspectiveTransform(pts1,pts2)
dst = cv2.warpPerspective(img,M,(1000,1000))

# Convert to grayscale and apply blur
gray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
gray = cv2.equalizeHist(gray)

img_blur = cv2.GaussianBlur(gray, (7, 7), 0)

# Apply Canny edge detector
edges = cv2.Canny(img_blur, 30, 60, apertureSize=3)

# Applying standard Hough Line Transform
lines = cv2.HoughLines(edges, 1, np.pi / 180, 150)

# Separate lines into horizontal and vertical
horizontal_lines = []
vertical_lines = []

for line in lines:
    rho, theta = line[0]
    if np.isclose(abs(theta), 0):
        horizontal_lines.append(line[0])
    elif np.isclose(abs(theta), np.pi / 2):
        vertical_lines.append(line[0])

# Cluster and merge horizontal lines
horizontal_clusters = cluster_lines(horizontal_lines, distance_threshold=15, angle_threshold=np.pi / 180)
merged_horizontal_lines = merge_clusters(horizontal_clusters)

# Cluster and merge vertical lines
vertical_clusters = cluster_lines(vertical_lines, distance_threshold=15, angle_threshold=np.pi / 180)
merged_vertical_lines = merge_clusters(vertical_clusters)

# Combine merged lines
merged_lines = merged_horizontal_lines + merged_vertical_lines

# Find intersection points of merged lines
intersection_points = get_intersection_points(merged_horizontal_lines, merged_vertical_lines)
sorted_points = sort_points(intersection_points)

print(f"Number of horizontal lines: {len(horizontal_lines):.2f}")
print(f"Number of vertical lines: {len(vertical_lines):.2f}")
print(f"Number of lines: {len(lines):.2f}")
print(f"Number of merged_lines: {len(merged_lines):.2f}")
print(f"Number of sorted points: {len(sorted_points):.2f}")

squares = find_squares(sorted_points, 1, 1)

for square in squares:
    top_left, top_right, bottom_left, bottom_right = square
    # You can now process each square. For example:
    cv2.rectangle(dst, top_left, bottom_right, (255, 0, 0), 4)

# Draw intersection points on the original image
for point in sorted_points:
    cv2.circle(dst, point, 5, (0, 255, 0), -1)

for idx, square in enumerate(squares):
    # Extract corners of the square
    top_left, top_right, bottom_left, bottom_right = square

    # Create a mask for the square
    mask = np.zeros_like(dst)
    roi_corners = np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.int32)
    cv2.fillPoly(mask, [roi_corners], (255, 255, 255))

    # Apply the mask to the original image
    square_image = cv2.bitwise_and(dst, mask)

    mean_intensity = np.mean(square_image)
    # Determine if the square is occupied based on mean intensity threshold
    occupied = mean_intensity > 5  # Adjust threshold as needed
    
    # Draw rectangle on the original image based on occupancy
    color = (0, 255, 0) if occupied else (0, 0, 255)
    cv2.rectangle(dst, top_left, bottom_right, color, thickness=2)


# Draw the merged lines on the image
# draw_lines(dst, merged_lines)

# Displaying the Image
cv2.imshow('Original Image', img)
cv2.imshow('Gray Scale', gray)
cv2.imshow('Transformed Image', dst)
cv2.imshow('Edges', edges)
cv2.waitKey(0)
cv2.destroyAllWindows()
