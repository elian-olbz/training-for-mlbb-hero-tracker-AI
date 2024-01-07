from ultralytics import YOLO

def train_yolo():
    model = YOLO("yolov8n.pt")
    model.train(data="data_custom.yaml", epochs=25, imgsz=640, batch=2)

if __name__ == '__main__':
    train_yolo()

#yolo task=detect mode=train epochs=100 data=data_custom.yaml model=yolov8m.pt imgsz=640 batch=4