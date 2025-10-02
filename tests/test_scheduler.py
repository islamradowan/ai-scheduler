import pytest
import pandas as pd
from collections import defaultdict
from app.scheduler_core import schedule

def test_schedule_basic():
    """Test basic scheduling functionality"""
    
    # Create minimal test data
    courses_df = pd.DataFrame([
        {'course_id': 'C001', 'code': 'MATH101', 'name': 'Mathematics'},
        {'course_id': 'C002', 'code': 'PHYS101', 'name': 'Physics'},
        {'course_id': 'C003', 'code': 'CHEM101', 'name': 'Chemistry'}
    ])
    
    students_df = pd.DataFrame([
        {'student_id': 'S001', 'name': 'Alice'},
        {'student_id': 'S002', 'name': 'Bob'},
        {'student_id': 'S003', 'name': 'Charlie'},
        {'student_id': 'S004', 'name': 'Diana'},
        {'student_id': 'S005', 'name': 'Eve'}
    ])
    
    enrollments_df = pd.DataFrame([
        {'student_id': 'S001', 'course_id': 'C001'},
        {'student_id': 'S001', 'course_id': 'C002'},
        {'student_id': 'S002', 'course_id': 'C002'},
        {'student_id': 'S002', 'course_id': 'C003'},
        {'student_id': 'S003', 'course_id': 'C001'},
        {'student_id': 'S004', 'course_id': 'C003'},
        {'student_id': 'S005', 'course_id': 'C001'}
    ])
    
    rooms_df = pd.DataFrame([
        {'room_id': 'R001', 'name': 'Room A', 'capacity': 30}
    ])
    
    config = {
        'exam_days': ['2024-05-01', '2024-05-02'],
        'exam_slots': [
            {'start_time': '09:00', 'end_time': '12:00'},
            {'start_time': '14:00', 'end_time': '17:00'}
        ],
        'optimization': {
            'population_size': 10,
            'generations': 5
        }
    }
    
    # Run scheduler
    result = schedule(courses_df, students_df, rooms_df, enrollments_df, config)
    
    # Basic assertions
    assert 'timetable' in result
    assert 'score' in result
    assert isinstance(result['timetable'], list)
    assert isinstance(result['score'], (int, float))
    
    # Should schedule all 3 courses
    assert len(result['timetable']) == 3
    
    # Each exam should have required fields
    for exam in result['timetable']:
        assert 'course_id' in exam
        assert 'slot_date' in exam
        assert 'slot_time' in exam
        assert 'assignments' in exam
        assert len(exam['assignments']) == 1  # Single assignment initially

def test_no_student_multiple_exams_same_day():
    """Test that no student has multiple exams on the same day"""
    
    courses_df = pd.DataFrame([
        {'course_id': 'C001', 'code': 'MATH101', 'name': 'Mathematics'},
        {'course_id': 'C002', 'code': 'PHYS101', 'name': 'Physics'},
        {'course_id': 'C003', 'code': 'CHEM101', 'name': 'Chemistry'}
    ])
    
    students_df = pd.DataFrame([
        {'student_id': 'S001', 'name': 'Alice'},
        {'student_id': 'S002', 'name': 'Bob'}
    ])
    
    # Student S001 enrolled in all 3 courses (high conflict)
    enrollments_df = pd.DataFrame([
        {'student_id': 'S001', 'course_id': 'C001'},
        {'student_id': 'S001', 'course_id': 'C002'},
        {'student_id': 'S001', 'course_id': 'C003'},
        {'student_id': 'S002', 'course_id': 'C001'}
    ])
    
    rooms_df = pd.DataFrame([
        {'room_id': 'R001', 'name': 'Room A', 'capacity': 30}
    ])
    
    config = {
        'exam_days': ['2024-05-01', '2024-05-02', '2024-05-03'],
        'exam_slots': [
            {'start_time': '09:00', 'end_time': '12:00'},
            {'start_time': '14:00', 'end_time': '17:00'}
        ],
        'optimization': {
            'population_size': 20,
            'generations': 10
        }
    }
    
    result = schedule(courses_df, students_df, rooms_df, enrollments_df, config)
    
    # Check that S001 doesn't have multiple exams on same day
    student_exam_days = defaultdict(list)
    
    for exam in result['timetable']:
        exam_date = exam['slot_date']
        for assignment in exam['assignments']:
            for student_id in assignment['students']:
                student_exam_days[student_id].append(exam_date)
    
    # S001 should have exams on different days
    s001_days = student_exam_days['S001']
    assert len(s001_days) == len(set(s001_days)), "Student S001 has multiple exams on the same day"

def test_schedule_with_minimal_config():
    """Test scheduling with minimal configuration"""
    
    courses_df = pd.DataFrame([
        {'course_id': 'C001', 'code': 'MATH101', 'name': 'Mathematics'}
    ])
    
    students_df = pd.DataFrame([
        {'student_id': 'S001', 'name': 'Alice'}
    ])
    
    enrollments_df = pd.DataFrame([
        {'student_id': 'S001', 'course_id': 'C001'}
    ])
    
    rooms_df = pd.DataFrame([
        {'room_id': 'R001', 'name': 'Room A', 'capacity': 30}
    ])
    
    # Minimal config
    config = {}
    
    result = schedule(courses_df, students_df, rooms_df, enrollments_df, config)
    
    # Should still work with defaults
    assert len(result['timetable']) == 1
    assert result['timetable'][0]['course_id'] == 'C001'
    assert len(result['timetable'][0]['assignments'][0]['students']) == 1

def test_empty_schedule():
    """Test scheduling with no courses"""
    
    courses_df = pd.DataFrame(columns=['course_id', 'code', 'name'])
    students_df = pd.DataFrame(columns=['student_id', 'name'])
    enrollments_df = pd.DataFrame(columns=['student_id', 'course_id'])
    rooms_df = pd.DataFrame([{'room_id': 'R001', 'name': 'Room A', 'capacity': 30}])
    
    config = {'optimization': {'population_size': 5, 'generations': 2}}
    
    result = schedule(courses_df, students_df, rooms_df, enrollments_df, config)
    
    # Should return empty timetable
    assert len(result['timetable']) == 0
    assert isinstance(result['score'], (int, float))