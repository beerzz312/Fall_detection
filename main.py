#  uvicorn main:app --reload

from typing import List
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import requests
import sqlite3


# SQLAlchemy setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base = declarative_base()

# Define Patient model
class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(String)
    cd = Column(String)
    pm = Column(String)
    ecall = Column(String)
    ad = Column(String)
    map = Column(String)

# Define Camera model
class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, index=True)
    ip = Column(String, index=True)
    username = Column(String)
    password = Column(String)

# Define Token model
class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True) # Ensure unique token
    
    class Config:
        from_attributes = True  

# Create database tables
# รันคำสั่งนี้เพื่อลบข้อมูลทั้งหมด
# Base.metadata.drop_all(bind=engine) 

Base.metadata.create_all(bind=engine)


# Add default token
def add_default_token(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        existing_token = session.query(Token).first()
        if not existing_token:
            default_token = Token(token="your_default_token")
            session.add(default_token)
            session.commit()
            print("Default token added to the database.")
        else:
            print("Token already exists in the database.")
    finally:
        session.close()

add_default_token(engine)

# FastAPI setup

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("./static/index.html")


# Pydantic model for patient data
class PatientData(BaseModel):
    name: str
    age: str
    cd: str
    pm: str
    ecall: str
    ad: str
    map: str
    
    class Config:
        orm_mode = True
        
# Pydantic model for updating patient data
class UpdatePatientData(BaseModel):
    name: str
    age: str
    cd: str
    pm: str
    ecall: str
    ad: str
    map: str
    
    class Config:
        orm_mode = True
        from_attributes = True

# Pydantic models for request and response
class CameraCreate(BaseModel):
    number: str
    ip: str
    username: str
    password: str

class CameraResponse(CameraCreate):
    id: int
    number: str
    ip: str
    username: str
    password: str

    class Config:
        orm_mode = True
        from_attributes = True

class TokenRequest(BaseModel):
    token: str

class TokenResponse(TokenRequest):
    id: int
    token: str

    class Config:
        orm_mode = True
        from_attributes = True

class ButtonState(BaseModel):
    is_pressed: bool

# Database session handling
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.mount("/static", StaticFiles(directory="static"), name="static")

# การเรียกใช้ GET หน้าหลัก
@app.get("/", operation_id="read_root_index")
def read_root():
    return FileResponse("./static/index.html")


@app.post("/patients/", response_model=PatientData, operation_id="create_patient")
def create_patient(patient_data: PatientData, db: Session = Depends(get_db)):
    db_patient = Patient(**patient_data.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@app.get("/patients/", response_model=List[PatientData])
def get_patients(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    patients = db.query(Patient).offset(skip).limit(limit).all()
    return [PatientData.from_orm(patient) for patient in patients]

# อัปเดตข้อมูลผู้ป่วย
@app.put("/patients/{patient_id}", response_model=PatientData)
async def update_patient(patient_id: int, patient_data: UpdatePatientData, db: Session = Depends(get_db)):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Update patient data
    db_patient.name = patient_data.name
    db_patient.age = patient_data.age
    db_patient.cd = patient_data.cd
    db_patient.pm = patient_data.pm
    db_patient.ecall = patient_data.ecall
    db_patient.ad = patient_data.ad
    db_patient.map = patient_data.map

    db.commit()
    db.refresh(db_patient)

    return db_patient


# Camera routes
@app.post("/cameras/", response_model=CameraResponse, operation_id="create_camera")
def create_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    db_camera = Camera(**camera.dict())
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera

@app.get("/cameras/", response_model=List[CameraResponse])
def get_cameras(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    cameras = db.query(Camera).offset(skip).limit(limit).all()
    return [CameraResponse.from_orm(camera) for camera in cameras]

@app.put("/cameras/{camera_id}", response_model=CameraResponse)
def update_camera(camera_id: int, camera: CameraCreate, db: Session = Depends(get_db)):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not db_camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    db_camera.number = camera.number
    db_camera.ip = camera.ip
    db_camera.username = camera.username
    db_camera.password = camera.password
    db.commit()
    db.refresh(db_camera)

    return db_camera

@app.delete("/cameras/{camera_id}")
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not db_camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    db.delete(db_camera)
    db.commit()

    return {"message": "Camera deleted"}

# Token routes
        
@app.post("/tokens/", response_model=TokenResponse)
def create_token(token: TokenRequest, db: Session = Depends(get_db)):
    # Validate unique token before saving
    existing_token = db.query(Token).filter(Token.token == token.token).first()
    if existing_token:
        raise HTTPException(status_code=400, detail="Duplicate token found. Please use a unique token.")

    db_token = Token(**token.dict())
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

@app.get("/tokens/", response_model=List[TokenResponse])
def get_tokens(db: Session = Depends(get_db)):
    tokens = db.query(Token).all()
    return [TokenResponse.from_orm(token) for token in tokens]

@app.put("/tokens/{token_id}", response_model=TokenResponse)
def update_token(token_id: int, token: TokenRequest, db: Session = Depends(get_db)):
    db_token = db.query(Token).filter(Token.id == token_id).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="Token not found")

    # Validate unique token before updating
    existing_token = db.query(Token).filter(Token.token == token.token, Token.id != token_id).first()
    if existing_token:
        raise HTTPException(status_code=400, detail="Duplicate token found. Please use a unique token.")

    db_token.token = token.token
    db.commit()
    db.refresh(db_token)
    return db_token

@app.delete("/tokens/{token}")
def delete_token(token: str, db: Session = Depends(get_db)):
    db_token = db.query(Token).filter(Token.token == token).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="Token not found")

    db.delete(db_token)
    db.commit()

    return {"message": "Token deleted"}

@app.get("/latest_token", response_model=TokenResponse)
def get_latest_token(db: Session = Depends(get_db)):
    latest_token = db.query(Token).order_by(Token.id.desc()).first()
    if latest_token:
        return TokenResponse.from_orm(latest_token)
    else:
        raise HTTPException(status_code=404, detail="No tokens found")
    
@app.post("/button")
async def receive_button_state(button_state: ButtonState):
    if button_state.is_pressed:
        requests.post(url, headers=headers, data={'message': msg})
        print("The button is pressed")
        # Insert button press into the database
        c.execute("INSERT INTO button_presses (is_pressed) VALUES (?)", (1,))
        conn.commit()
    return {"message": "Button state received"}

@app.get("/button_presses")
async def get_button_presses():
    # Retrieve all button presses from the database
    c.execute("SELECT * FROM button_presses")
    button_presses = c.fetchall()
    # Create a list of button press states
    button_presses_list = []
    for button_press in button_presses:
        button_presses_list.append({"id": button_press[0], "is_pressed": bool(button_press[1])})
    return {"button_presses": button_presses_list}
    


# Line Notify configuration

db = SessionLocal()
latest_token_obj = get_latest_token(db)
db.close()

# Line Notify configuration
url = 'https://notify-api.line.me/api/notify'
token = latest_token_obj.token if latest_token_obj else ''
headers = {'content-type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer ' + token}
msg = "ยกเลิกการแจ้งเตือน \nผู้ประสบอุบัติเหตช่วยเหลือตัวเองหรือได้รับการช่วยเหลือเเล้ว"

# Connect to SQLite3 database
conn = sqlite3.connect('button.db')
c = conn.cursor()

# Create button_presses table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS button_presses (id INTEGER PRIMARY KEY AUTOINCREMENT, is_pressed INTEGER)''')
conn.commit()
