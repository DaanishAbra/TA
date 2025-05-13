import cv2
from datetime import datetime
from ultralytics import YOLO
import numpy as np
import easyocr
import threading

# Konstanta
FPS = 30
DISTANCE_PER_PIXEL = 0.00625  # 1 meter ≈ 160 piksel pada ketinggian 4 meter
SPEED_THRESHOLD = 20  # km/jam
CONFIDENCE_THRESHOLD = 0.5

# Inisialisasi model dan OCR
model = YOLO("yolov8n.pt")
reader = easyocr.Reader(['en'])

# Kelas objek yang ingin dideteksi
COCO_CLASSES = {
    0: "Orang",
    2: "Mobil",
    3: "Motor"
}

def match_objects(prev_boxes, new_boxes):
    matched_objects = {}
    for new_id, data in new_boxes.items():
        if isinstance(data, dict) and "bbox" in data:
            matched_objects[new_id] = data
    return matched_objects

def calculate_speed(prev_center, curr_center, fps, distance_per_pixel):
    distance_px = np.sqrt((curr_center[0] - prev_center[0]) ** 2 + (curr_center[1] - prev_center[1]) ** 2)
    distance_m = distance_px * distance_per_pixel
    speed_mps = distance_m * fps
    speed_kmh = speed_mps * 3.6
    return speed_kmh

def detect_license_plate(image, bbox):
    if isinstance(bbox, tuple) and len(bbox) == 4:
        x1, y1, x2, y2 = bbox
        plate_region = image[y1:y2, x1:x2]
        if plate_region.size == 0:
            return "Unknown"
        gray_plate = cv2.cvtColor(plate_region, cv2.COLOR_BGR2GRAY)
        results = reader.readtext(gray_plate)
        if results:
            return results[0][-2]
    return "Unknown"

def process_camera(camera_index, window_name):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Error: Kamera {camera_index} tidak bisa dibuka.")
        return

    prev_positions = {}

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        new_positions = {}

        for r in results:
            for box, cls, conf in zip(r.boxes.xyxy, r.boxes.cls, r.boxes.conf):
                class_id = int(cls)
                if conf > CONFIDENCE_THRESHOLD and class_id in COCO_CLASSES:
                    x1, y1, x2, y2 = map(int, box)
                    center = ((x1 + x2) // 2, (y1 + y2) // 2)
                    label = COCO_CLASSES[class_id]

                    data = {
                        "bbox": (x1, y1, x2, y2),
                        "label": label,
                        "center": center
                    }

                    new_positions[len(new_positions)] = data

                    if label in ["Mobil", "Motor"]:
                        plate_number = detect_license_plate(frame, (x1, y2 - 30, x2, y2))
                        cv2.putText(frame, f"{label} - {plate_number}", (x1, y1 - 25),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    else:
                        cv2.putText(frame, label, (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        matched_objects = match_objects(prev_positions, new_positions)

        for object_id, data in matched_objects.items():
            if isinstance(data, dict) and "bbox" in data and "center" in data:
                bbox = data["bbox"]
                label = data["label"]
                center = data["center"]
                x1, y1, x2, y2 = bbox

                if object_id in prev_positions:
                    prev_center = prev_positions[object_id]["center"]

                    if label in ["Mobil", "Motor"]:
                        speed = calculate_speed(prev_center, center, FPS, DISTANCE_PER_PIXEL)
                        color = (0, 0, 255) if speed > SPEED_THRESHOLD else (255, 255, 255)
                        cv2.putText(frame, f"{speed:.2f} km/h", (x1, y2 + 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        prev_positions = new_positions
        cv2.imshow(window_name, frame)

        if cv2.waitKey(1) & 0xFF == ord('x'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Jalankan dua kamera
thread1 = threading.Thread(target=process_camera, args=(0, "Kamera 1"))
thread2 = threading.Thread(target=process_camera, args=(1, "Kamera 2"))

thread1.start()
thread2.start()

thread1.join()
thread2.join()
