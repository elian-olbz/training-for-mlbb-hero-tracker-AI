import sys
import cv2
import csv
import threading
from math import ceil
from ultralytics import YOLO
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QSizePolicy, QTextEdit, QScrollArea
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QSize

class VideoAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize the YOLOv8 model
        self.model = YOLO('models/yolov8_custom.pt')

        # Create the main widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create a scroll area to contain the video display
        self.video_scroll_area = QScrollArea(self)
        self.layout.addWidget(self.video_scroll_area)

        # Create a widget to display video frames
        self.video_widget = QWidget(self)
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.video_widget.setFixedSize(QSize(640, 480))  # Set a fixed size for the video widget
        self.video_scroll_area.setWidget(self.video_widget)

        # Create a label to display video frames
        self.video_label = QLabel(self.video_widget)
        self.video_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.video_label.setFixedSize(QSize(640, 480))  # Set a fixed size for the video label
        self.video_widget.setLayout(QVBoxLayout())
        self.video_widget.layout().addWidget(self.video_label)

        # Create an "Open Video" button
        self.open_video_button = QPushButton("Open Video", self)
        self.open_video_button.clicked.connect(self.open_video_file)
        self.layout.addWidget(self.open_video_button)

        # Create a start button
        self.start_button = QPushButton("Start Prediction", self)
        self.start_button.clicked.connect(self.start_prediction)
        self.layout.addWidget(self.start_button)

        # Create a crop button
        self.crop_button = QPushButton("Crop Video", self)
        self.crop_button.clicked.connect(self.crop_video)
        self.layout.addWidget(self.crop_button)

        # Create a stop and exit button
        self.stop_and_exit_button = QPushButton("Stop and Exit", self)
        self.stop_and_exit_button.clicked.connect(self.stop_and_exit)
        self.layout.addWidget(self.stop_and_exit_button)

        # Create a console output area
        self.console_label = QTextEdit(self)
        self.console_label.setReadOnly(True)
        self.console_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.console_label)

        # Initialize video capture variables
        self.cap = None
        self.video_path = ""
        self.csv_filename = 'data/locx.csv'  # Change the location of the CSV file
        self.csv_file = None
        self.csv_writer = None
        self.frame_count = 0

        # Initialize cropping variables
        self.is_cropping = False
        self.crop_coordinates = None
        self.original_frame = None  # Store the original frame when cropping

        # Initialize the prediction thread and flag
        self.prediction_thread = None
        self.is_running = False

        # Initialize the GUI
        self.init_ui()

    def init_ui(self):
        # Set the window properties
        self.setWindowTitle("Video Analyzer")
        self.setGeometry(100, 100, 800, 800)  # Adjust the window size as needed
        self.show()

    def open_video_file(self):
        video_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv);;All Files (*)")
        if video_path:
            self.video_path = video_path

            # Load and display the first frame
            self.cap = cv2.VideoCapture(self.video_path)
            success, frame = self.cap.read()
            if success:
                self.original_frame = frame
                self.display_frame(frame)

    def crop_video(self):
        # Set the cropping mode and prompt the user to select the region
        self.is_cropping = True
        self.crop_coordinates = cv2.selectROI("Select ROI", self.original_frame)
        cv2.destroyAllWindows()  # Close the ROI selector window

    def display_frame(self, frame):
        # Convert the OpenCV frame to a QImage
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)

        # Scale the video display to fit the container size
        scaled_image = q_image.scaled(self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        # Set the QImage in the QLabel
        self.video_label.setPixmap(QPixmap.fromImage(scaled_image))

    def start_prediction(self):
        if not self.cap or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.video_path)

        if not self.cap.isOpened():
            return

        if not self.csv_file:
            self.csv_file = open(self.csv_filename, 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(['Frame', 'Class', 'X', 'Y'])

        # Create a thread for running the prediction
        self.is_running = True
        self.prediction_thread = threading.Thread(target=self.run_prediction)
        self.prediction_thread.start()

    def run_prediction(self):
        while self.cap.isOpened() and self.is_running:  # Check the flag before each iteration
            success, frame = self.cap.read()

            if success:
                self.frame_count += 1

                # Use the cropped frame if cropping is active
                if self.is_cropping:
                    frame = frame[self.crop_coordinates[1]:self.crop_coordinates[1] + self.crop_coordinates[3],
                                  self.crop_coordinates[0]:self.crop_coordinates[0] + self.crop_coordinates[2]]

                results = self.model.predict(frame, conf=0.5)

                for r in results:
                    for box in r.boxes:
                        class_id = box.cls
                        pred = box.xyxy[0]
                        x_min = pred[0].item()
                        y_min = pred[1].item()
                        x_max = pred[2].item()
                        y_max = pred[3].item()
                        self.csv_writer.writerow([self.frame_count, self.model.names[int(class_id)], ceil((x_min + x_max) / 2), ceil((y_min + y_max) / 2)])

                annotated_frame = results[0].plot()

                # Display the annotated frame in the QLabel
                self.display_frame(annotated_frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                break

    def stop_and_exit(self):
        # Set the flag to stop the prediction thread
        self.is_running = False

        # Stop video capture if it's running
        if self.cap and self.cap.isOpened():
            self.cap.release()

        # Close the CSV file if it's open
        if self.csv_file:
            self.csv_file.close()

        # Wait for the prediction thread to finish before exiting
        if self.prediction_thread and self.prediction_thread.is_alive():
            self.prediction_thread.join()

        # Close the application
        sys.exit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoAnalyzerApp()
    sys.exit(app.exec())
