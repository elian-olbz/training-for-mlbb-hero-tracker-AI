from ultralytics import YOLO


model = YOLO('best.pt')  # load a custom trained

# Export the model
model.export(format='onnx')