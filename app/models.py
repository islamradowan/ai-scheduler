from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, DateTime, Time, Date
from sqlalchemy.orm import relationship
from app.database import Base

class Student(Base):
    __tablename__ = "students"
    student_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    batch_type = Column(String)
    year = Column(Integer)
    section = Column(String)

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    semester = Column(Integer)
    department = Column(String)
    exam_type = Column(String)
    priority_flag = Column(Boolean, default=False)

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey("students.student_id"))
    course_id = Column(Integer, ForeignKey("courses.id"))

class Room(Base):
    __tablename__ = "rooms"
    room_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    num_columns = Column(Integer, nullable=False)

class Timeslot(Base):
    __tablename__ = "timeslots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

class ExamAssignment(Base):
    __tablename__ = "exam_assignments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    slot_id = Column(Integer, ForeignKey("timeslots.id"))

class ExamRoom(Base):
    __tablename__ = "exam_rooms"
    id = Column(Integer, primary_key=True, autoincrement=True)
    exam_assignment_id = Column(Integer, ForeignKey("exam_assignments.id"))
    room_id = Column(String, ForeignKey("rooms.room_id"))

class SeatAssignment(Base):
    __tablename__ = "seat_assignments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    exam_assignment_id = Column(Integer, ForeignKey("exam_assignments.id"))
    room_id = Column(String, ForeignKey("rooms.room_id"))
    student_id = Column(String, ForeignKey("students.student_id"))
    row = Column(Integer, nullable=False)
    column = Column(Integer, nullable=False)

class Invigilator(Base):
    __tablename__ = "invigilators"
    teacher_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    availability = Column(JSON)

class InvigilatorAssignment(Base):
    __tablename__ = "invigilator_assignments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    exam_assignment_id = Column(Integer, ForeignKey("exam_assignments.id"))
    room_id = Column(String, ForeignKey("rooms.room_id"))
    teacher_id = Column(String, ForeignKey("invigilators.teacher_id"))
    load_balance_score = Column(Integer)