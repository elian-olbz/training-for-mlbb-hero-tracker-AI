from ultralytics import YOLO

model = YOLO("yolov8_custom.pt")
model.predict(show=True, conf=0.5, iou=0.5, nms=True, max_det=10, save=True, source="C:/Users/Marlon/Desktop/vid/im4.jpg", line_width=2)

#yolo task=detect mode=predict model=best.pt show=True conf=0.75 source=C:/Users/Marlon/Desktop/vid/bo.mp4 stream=True