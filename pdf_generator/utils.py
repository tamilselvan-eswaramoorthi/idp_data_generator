import cv2 
import json

def combine_bounding_boxes(bounding_boxes):
    # Initialize with extreme values to find minimum and maximum coordinates
    x_min_combined, y_min_combined = float('inf'), float('inf')
    x_max_combined, y_max_combined = float('-inf'), float('-inf')

    # Iterate through each bounding box
    for bbox in bounding_boxes:
        x_min, y_min, x_max, y_max = bbox
        x_min_combined = min(x_min_combined, x_min)
        y_min_combined = min(y_min_combined, y_min)
        x_max_combined = max(x_max_combined, x_max)
        y_max_combined = max(y_max_combined, y_max)

    # Create the combined bounding box
    combined_bbox = (x_min_combined, y_min_combined, x_max_combined, y_max_combined)
    return combined_bbox

def draw_bb(name):
    frame = cv2.imread(f"data/{name}.png")
    for d in json.load(open(f"data/{name}.json", "rb")):
        x1, y1, x2, y2 = d['bbox']
        text = d['text']
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2) ), (0, 0, 255), thickness = 1)
    cv2.imwrite('temp.png', frame)