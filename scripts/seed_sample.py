#!/usr/bin/env python3
"""
Seed script to populate database with sample data for testing.
"""

import os
import sys
import pandas as pd

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal, create_db
from app.crud import create_student, create_course, create_enrollment, create_room
from app.parser import parse_csvs

def seed_database():
    """Seed database with sample CSV data"""
    
    # Ensure database exists
    create_db()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Parse sample CSV files
        data_dir = "data"
        students_path = os.path.join(data_dir, "sample_student.csv")
        courses_path = os.path.join(data_dir, "sample_course.csv")
        rooms_path = os.path.join(data_dir, "sample_room.csv")
        
        print("Parsing sample CSV files...")
        parsed_data = parse_csvs(students_path, courses_path, rooms_path)
        
        students_df = parsed_data['students']
        courses_df = parsed_data['courses']
        rooms_df = parsed_data['rooms']
        enrollments_df = parsed_data['enrollments']
        
        # Insert students
        print(f"Inserting {len(students_df)} students...")
        for _, student in students_df.iterrows():
            create_student(
                db,
                student_id=student['student_id'],
                name=student['name'],
                batch_type=student.get('batch_type'),
                year=student.get('year'),
                section=student.get('section')
            )
        
        # Insert courses
        print(f"Inserting {len(courses_df)} courses...")
        for _, course in courses_df.iterrows():
            create_course(
                db,
                code=course['code'],
                name=course['name'],
                semester=course.get('semester'),
                department=course.get('department'),
                exam_type=course.get('exam_type'),
                priority_flag=course.get('priority_flag', False)
            )
        
        # Insert rooms
        print(f"Inserting {len(rooms_df)} rooms...")
        for _, room in rooms_df.iterrows():
            create_room(
                db,
                room_id=room['room_id'],
                name=room['name'],
                capacity=room['capacity'],
                num_columns=room.get('num_columns', 4)
            )
        
        # Insert enrollments
        print(f"Inserting {len(enrollments_df)} enrollments...")
        for _, enrollment in enrollments_df.iterrows():
            create_enrollment(
                db,
                student_id=enrollment['student_id'],
                course_id=enrollment['course_id']
            )
        
        print("Sample data seeded successfully!")
        print(f"- Students: {len(students_df)}")
        print(f"- Courses: {len(courses_df)}")
        print(f"- Rooms: {len(rooms_df)}")
        print(f"- Enrollments: {len(enrollments_df)}")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()