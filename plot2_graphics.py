import sys
import csv
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView
from PyQt6.QtGui import QPixmap, QImage, QBrush
from PyQt6.QtCore import Qt, QTimer

class ObjectMovementVisualization(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Object Movement Visualization")
        self.setGeometry(100, 100, 720, 720)  # Set the window size to 720x720

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        # Load and set the background image
        background_image_path = "images/map.png"  # Replace with your background image file path
        self.load_background_image(background_image_path)

        self.dataset_filename = "data/loc1.csv"  # Replace with your dataset file's path
        self.current_frame = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_objects)
        self.timer.start(100)  # Adjust the timer interval (milliseconds) as needed for your frame rate

        self.load_class_images()
        self.draw_objects_from_dataset()

    def load_background_image(self, image_path):
        image = QImage(image_path)
        pixmap = QPixmap.fromImage(image)
        
        # Resize the pixmap to match the window's size
        pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
        
        brush = QBrush(pixmap)
        self.scene.setBackgroundBrush(brush)

    def load_class_images(self):
        self.class_images = {}
        class_names = set()
        
        with open(self.dataset_filename, "r") as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row

            for row in csv_reader:
                obj_class = row[1]
                class_names.add(obj_class)

        for class_name in class_names:
            image_path = f"images/{class_name}.jpg"  # Assuming the image files are named after the class names
            pixmap = QPixmap(image_path)
            self.class_images[class_name] = pixmap

    def draw_objects_from_dataset(self):
        with open(self.dataset_filename, "r") as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row
            self.data = list(csv_reader)

    def update_objects(self):
        if self.current_frame < len(self.data):
            self.scene.clear()
            for row in self.data[self.current_frame:min(self.current_frame + 10, len(self.data))]:
                frame, obj_class, x, y = row[0], row[1], int(row[2]), int(row[3])
                if obj_class in self.class_images:
                    pixmap = self.class_images[obj_class]
                    item = self.scene.addPixmap(pixmap)
                    item.setPos(x, y)
            self.current_frame += 10  # Increment by 10 frames
        else:
            self.timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ObjectMovementVisualization()
    window.show()
    sys.exit(app.exec())
