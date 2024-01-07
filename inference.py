import cv2
import csv
from math import ceil
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO('models/yolov8_custom.pt')

# Open the video file
video_path = "C:/Users/Marlon/Desktop/vid/bo2.mp4"
cap = cv2.VideoCapture(video_path)

# Initialize a CSV file for saving coordinates
csv_filename = 'images/locx.csv'
csv_file = open(csv_filename, 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Frame', 'Class', 'X', 'Y'])

# Loop through the video frames
frame_count = 0
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        frame_count += 1

        # Run YOLOv8 inference on the frame
        results = model.predict(frame, conf=0.5)

        # Extract and save prediction coordinates to CSV
        for r in results:
            for box in r.boxes:
                class_id = box.cls
                pred = box.xyxy[0]
                x_min = pred[0].item()
                y_min = pred[1].item()
                x_max = pred[2].item()
                y_max = pred[3].item()
                csv_writer.writerow([frame_count, model.names[int(class_id)], ceil((x_min + x_max) / 2), ceil((y_min + y_max) / 2)]) #frame.shape[0] - 

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the annotated frame
        cv2.imshow("YOLOv8 Inference", annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object, close the CSV file, and close the display window
cap.release()
csv_file.close()
cv2.destroyAllWindows()
