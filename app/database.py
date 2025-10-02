from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./data/scheduler.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db():
    from app.models import Student, Course, Enrollment, Room, Timeslot, ExamAssignment, ExamRoom, SeatAssignment, Invigilator, InvigilatorAssignment
    Base.metadata.create_all(bind=engine)