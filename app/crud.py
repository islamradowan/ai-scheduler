from sqlalchemy.orm import Session
from app.models import Student, Course, Enrollment, Room

def create_student(db: Session, student_id: str, name: str, batch_type: str = None, year: int = None, section: str = None):
    student = Student(student_id=student_id, name=name, batch_type=batch_type, year=year, section=section)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

def get_student(db: Session, student_id: str):
    return db.query(Student).filter(Student.student_id == student_id).first()

def create_course(db: Session, code: str, name: str, semester: int = None, department: str = None, exam_type: str = None, priority_flag: bool = False):
    course = Course(code=code, name=name, semester=semester, department=department, exam_type=exam_type, priority_flag=priority_flag)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

def get_course(db: Session, course_id: int):
    return db.query(Course).filter(Course.id == course_id).first()

def create_enrollment(db: Session, student_id: str, course_id: int):
    enrollment = Enrollment(student_id=student_id, course_id=course_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment

def get_enrollments(db: Session):
    return db.query(Enrollment).all()

def create_room(db: Session, room_id: str, name: str, capacity: int, num_columns: int):
    room = Room(room_id=room_id, name=name, capacity=capacity, num_columns=num_columns)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

def get_room(db: Session, room_id: str):
    return db.query(Room).filter(Room.room_id == room_id).first()