# main
from ultralytics import YOLO
import cv2
import torch
import numpy as np
import requests
import time
import pyaudio
import wave
import threading
import sqlite3
from main import Camera, Patient, SessionLocal, get_latest_token
from sqlalchemy import create_engine, select
from main import Camera, SessionLocal, get_latest_token

global falldetected
falldetected = 0

global timedetected
timedetected = 0

global fall_count
fall_count = 0

# LINE token
db = SessionLocal()
latest_token_obj = get_latest_token(db)
db.close()

# Line Notify configuration
url = 'https://notify-api.line.me/api/notify'
token = latest_token_obj.token if latest_token_obj else ''

print(time.time())

device = torch.device("cuda:0")

# model = YOLO(model='yolov-fallX.pt')
model = YOLO(model='trained_model.pt')

# Replace with your database connection details
engine = create_engine("sqlite:////test.db")
with engine.connect() as conn:
    stmt = select(Patient).limit(1)  # Limit to 1 patient
    result = conn.execute(stmt).fetchone()
    
if result:
    patient = result
    message = f"{patient.name} \nอายุ {patient.age} ปี \nโรคประจำตัว {patient.cd} \nยาที่แพ้ {patient.pm} \nเบอร์โทรฉุกเฉิน - {patient.ecall} \nที่ {patient.ad} \n{patient.map}"
else:
        messages = "No patient data found in the database."


def get_first_camera(db):
    return db.query(Camera).order_by(Camera.id).first()

db = SessionLocal()
latest_token_obj = get_latest_token(db)
db.close()

# Get the first camera from the database
with SessionLocal() as db:
    first_camera = get_first_camera(db)
    if first_camera:
        user = first_camera.username
        password = first_camera.password
        ip = first_camera.ip
        cap1 = cv2.VideoCapture(f'rtsp://{user}:{password}@{ip}:554/stream1')  # กล้องในห้องนอน
    else:
        print("No cameras found in the database.")

# Get the second camera from the database
def get_second_camera(db):
    return db.query(Camera).order_by(Camera.id).offset(1).first()

with SessionLocal() as db:
    second_camera = get_second_camera(db)
    if second_camera:
        user = second_camera.username
        password = second_camera.password
        ip = second_camera.ip
        cap2 = cv2.VideoCapture(f'rtsp://admin:%40EH3319%262awr@{ip}/user=admin_password=%40EH3319%262awr_channel=1_stream=0.sdp')
        # Use the cap2 object for further processing
    else:
        print("No second camera found in the database.")


# กำหนดตัวแปร global เพื่อเก็บสถานะของการเล่นเสียง
is_playing = False

# ฟังก์ชันเล่นเสียงไปเลือยๆ
def play_alert_sound():
    global is_playing
    
    # ตรวจสอบว่าไม่มีการเล่นเสียงในขณะนี้
    if not is_playing:
        # เปลี่ยนสถานะการเล่นเสียงเป็น True
        is_playing = True
        
        # เริ่มเล่นเสียงในเธรดใหม่
        threading.Thread(target=_play_alert_sound).start()

# ฟังก์ชันที่ใช้เล่นเสียงจริง ๆ
def _play_alert_sound():
    try:
        # เปิดไฟล์เสียง
        wav_file = wave.open('emergency.wav', 'rb')

        # ตั้งค่าการเล่นเสียง
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wav_file.getsampwidth()),
                        channels=wav_file.getnchannels(),
                        rate=wav_file.getframerate(),
                        output=True)

        # เล่นเสียง
        data = wav_file.readframes(1024)
        while data:
            stream.write(data)
            data = wav_file.readframes(1024)

        # ปิดการเล่นเสียง
        stream.stop_stream()
        stream.close()
        p.terminate()
        
    finally:
        # เปลี่ยนสถานะการเล่นเสียงเป็น False เมื่อเสร็จสิ้น
        global is_playing
        is_playing = False

fall_count = 0  # นับจำนวนครั้งที่ตรวจพบการล้ม
start_time = time.time()  # เวลาเริ่มต้นการตรวจสอบล้ม
while True:
   ret1, frame1 = cap1.read()
   ret2, frame2 = cap2.read()

   if not ret1 or not ret2:
       break

   results1 = model.predict(source=frame1, conf=0.25)
   results2 = model.predict(source=frame2, conf=0.25)

   myimage1 = frame1.copy()
   myimage2 = frame2.copy()

   info1 = results1[0].boxes
   info2 = results2[0].boxes

   if falldetected == 0:
       for box in info1:
           class_name = results1[0].names[box.cls[0].item()]
           conf = box.conf[0].item()
           if class_name == "Fall":
                fall_count += 1
               # ตรวจสอบว่ามีการล้มต่อเนื่องเป็นเวลากี่วินาที
                elapsed_time1 = time.time() - start_time
                if fall_count >= 500 and elapsed_time1 >= 5: 
                    print("zxcv " + str(fall_count))
                    cv2.imwrite("fall_detection1.jpg", frame1)
                    try:
                        message 
                        headers = {"Authorization": f"Bearer {token}"}
                        files = {"imageFile": open("fall_detection1.jpg", "rb")}
                        data = {"message": message}
                        play_alert_sound()
                        requests.post(url, headers=headers, files=files, data=data)
                    except requests.exceptions.RequestException as e:
                        print("Error sending LINE Notify:", e)
                     # รีเซ็ตตัวแปรหลังจากส่งการแจ้งเตือน
                    fall_count = 0
                    start_time = time.time()
                    
                    # รอจนกว่าจะผ่านเงื่อนไขที่กำหนด
                    while falldetected == 1 and (time.time() - timedetected) <= 150:
                        pass
                    
                    falldetected = 0  # รีเซ็ตตัวแปร falldetected เพื่อให้สามารถตรวจจับการล้มใหม่ได้
                    
                    break

       for box in info2:
           class_name = results2[0].names[box.cls[0].item()]
           conf = box.conf[0].item()
           if class_name == "Fall":
                fall_count += 1
               # ตรวจสอบว่ามีการล้มต่อเนื่องเป็นเวลากี่วินาที
                elapsed_time1 = time.time() - start_time
                if fall_count >= 1500 and elapsed_time1 >= 60:  # 100 เฟรม = 10 วินาที (เมื่อใช้วิดีโอที่มีเฟรมเรทเป็น 10 เฟรมต่อวินาที)
                    print("zxcv " + str(fall_count))
                    cv2.imwrite("fall_detection2.jpg", frame2)
                    try:
                        message 
                        headers = {"Authorization": f"Bearer {token}"}
                        files = {"imageFile": open("fall_detection2.jpg", "rb")}
                        data = {"message": message}
                        play_alert_sound()
                        requests.post(url, headers=headers, files=files, data=data)
                    except requests.exceptions.RequestException as e:
                        print("Error sending LINE Notify:", e)
                     # รีเซ็ตตัวแปรหลังจากส่งการแจ้งเตือน
                    fall_count = 0
                    start_time = time.time()
                    
                    # รอจนกว่าจะผ่านเงื่อนไขที่กำหนด
                    while falldetected == 1 and (time.time() - timedetected) <= 150:
                        pass
                    
                    falldetected = 0  # รีเซ็ตตัวแปร falldetected เพื่อให้สามารถตรวจจับการล้มใหม่ได้
                    
                    break
        
   for box in info1:
       class_name = results1[0].names[box.cls[0].item()]
       conf = box.conf[0].item()
       if class_name != "Fall":
           coor = box.xyxy[0].tolist()
           coor = [round(x) for x in coor]
           text = f"{class_name}{conf:0.2f}"
           myimage1 = cv2.putText(myimage1, text, (coor[0] + 5, coor[1] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                  (255, 255, 255), 1, cv2.LINE_AA)
           myimage1 = cv2.rectangle(myimage1, (coor[0], coor[1]), (coor[2], coor[3]), (255, 255, 0), 2)
           

   for box in info2:
       class_name = results2[0].names[box.cls[0].item()]
       conf = box.conf[0].item()
       if class_name != "Fall":
           coor = box.xyxy[0].tolist()
           coor = [round(x) for x in coor]
           text = f"{class_name}{conf:0.2f}"
           myimage2 = cv2.putText(myimage2, text, (coor[0] + 5, coor[1] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                  (255, 255, 255), 1, cv2.LINE_AA)
           myimage2 = cv2.rectangle(myimage2, (coor[0], coor[1]), (coor[2], coor[3]), (255, 255, 0), 2)

   # Create a new window to display the images
   cv2.namedWindow("2222", cv2.WINDOW_NORMAL)
   cv2.namedWindow("1315", cv2.WINDOW_NORMAL)

   # Show the images in the windows
   cv2.imshow("2222", myimage1)
   cv2.imshow("1315", myimage2)

   # Resize the windows
   cv2.resizeWindow("2222", 800, 600)
   cv2.resizeWindow("1315", 800, 600)
   if cv2.waitKey(1) & 0xFF == ord('q'):
       break

cap1.release()
cap2.release()
cv2.destroyAllWindows()