import pytest
import pandas as pd
import tempfile
import os
from app.parser import parse_csvs

def test_parse_csvs_basic():
    """Test basic CSV parsing functionality"""
    
    # Create temporary CSV files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Students CSV
        students_data = """student_id,name,batch_type,year,section,enrolled_courses
S001,Alice,Regular,2023,A,MATH101 PHYS101
S002,Bob,Regular,2023,B,PHYS101,CHEM101
S003,Charlie,Regular,2023,A,MATH101"""
        
        students_path = os.path.join(temp_dir, "students.csv")
        with open(students_path, 'w') as f:
            f.write(students_data)
        
        # Courses CSV
        courses_data = """course_id,code,name,semester,department
C001,MATH101,Mathematics,1,Science
C002,PHYS101,Physics,1,Science
C003,CHEM101,Chemistry,1,Science"""
        
        courses_path = os.path.join(temp_dir, "courses.csv")
        with open(courses_path, 'w') as f:
            f.write(courses_data)
        
        # Rooms CSV
        rooms_data = """room_id,name,capacity,num_columns
R001,Room A,30,5
R002,Room B,25,4"""
        
        rooms_path = os.path.join(temp_dir, "rooms.csv")
        with open(rooms_path, 'w') as f:
            f.write(rooms_data)
        
        # Test parsing
        result = parse_csvs(students_path, courses_path, rooms_path)
        
        # Assertions
        assert 'students' in result
        assert 'courses' in result
        assert 'rooms' in result
        assert 'enrollments' in result
        
        # Check data integrity
        assert len(result['students']) == 3
        assert len(result['courses']) == 3
        assert len(result['rooms']) == 2
        assert len(result['enrollments']) == 5  # S001: 2, S002: 2, S003: 1
        
        # Check column normalization
        assert 'student_id' in result['students'].columns
        assert 'course_id' in result['courses'].columns
        assert 'room_id' in result['rooms'].columns

def test_parse_csvs_missing_columns():
    """Test error handling for missing required columns"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Invalid students CSV (missing required column)
        students_data = """id,name
S001,Alice"""
        
        students_path = os.path.join(temp_dir, "students.csv")
        with open(students_path, 'w') as f:
            f.write(students_data)
        
        courses_data = """course_id,code,name
C001,MATH101,Mathematics"""
        
        courses_path = os.path.join(temp_dir, "courses.csv")
        with open(courses_path, 'w') as f:
            f.write(courses_data)
        
        rooms_data = """room_id,name,capacity
R001,Room A,30"""
        
        rooms_path = os.path.join(temp_dir, "rooms.csv")
        with open(rooms_path, 'w') as f:
            f.write(rooms_data)
        
        # Should raise ValueError for missing student_id column
        with pytest.raises(ValueError, match="Missing required column"):
            parse_csvs(students_path, courses_path, rooms_path)

def test_enrollments_parsing():
    """Test enrollment parsing with different separators"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Students with different separators
        students_data = """student_id,name,enrolled_courses
S001,Alice,MATH101;PHYS101
S002,Bob,PHYS101|CHEM101
S003,Charlie,MATH101/CHEM101"""
        
        students_path = os.path.join(temp_dir, "students.csv")
        with open(students_path, 'w') as f:
            f.write(students_data)
        
        courses_data = """course_id,code,name
C001,MATH101,Mathematics
C002,PHYS101,Physics
C003,CHEM101,Chemistry"""
        
        courses_path = os.path.join(temp_dir, "courses.csv")
        with open(courses_path, 'w') as f:
            f.write(courses_data)
        
        rooms_data = """room_id,name,capacity
R001,Room A,30"""
        
        rooms_path = os.path.join(temp_dir, "rooms.csv")
        with open(rooms_path, 'w') as f:
            f.write(rooms_data)
        
        result = parse_csvs(students_path, courses_path, rooms_path)
        
        # Should parse 6 enrollments (2 per student)
        assert len(result['enrollments']) == 6
        
        # Check specific enrollments
        enrollments = result['enrollments']
        assert len(enrollments[enrollments['student_id'] == 'S001']) == 2
        assert len(enrollments[enrollments['student_id'] == 'S002']) == 2
        assert len(enrollments[enrollments['student_id'] == 'S003']) == 2