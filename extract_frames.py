import cv2
import os

# Path to the video file
video_path = 'C:/Users/Marlon/Desktop/vid/bo.mp4'

# Directory to save extracted frames
output_dir = 'C:/Users/Marlon/Desktop/vid/output_frames/blck_onic_g6/'
os.makedirs(output_dir, exist_ok=True)

# Maximum number of frames to extract per video
max_frames = 550

# Open the video file
cap = cv2.VideoCapture(video_path)

# Get total number of frames in the video
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Calculate the frame skip interval to achieve max_frames
frame_skip = max(1, total_frames // max_frames)

frame_count = 0
frame_index = 0

while True:
    # Read a frame from the video
    ret, frame = cap.read()
    
    # Break the loop if no more frames are available
    if not ret:
        break
    
    # Save the frame if it's within the desired frame range
    if frame_count % frame_skip == 0:
        output_path = os.path.join(output_dir, f'frame_{frame_index:04d}.jpg')
        cv2.imwrite(output_path, frame)
        frame_index += 1
    
    frame_count += 1

    # Break the loop if max_frames frames have been extracted
    if frame_index >= max_frames:
        break

# Release the video capture
cap.release()

print(f'{frame_index} frames extracted.')
