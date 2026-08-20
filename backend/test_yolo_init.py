from ultralytics import YOLO
try:
    model = YOLO("yolov8n.pt")
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
