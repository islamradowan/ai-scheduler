import pandas as pd
import re
import os

def parse_csvs(students_csv_path, courses_csv_path, rooms_csv_path):
    """Parse CSV files and return normalized DataFrames"""
    
    # Read CSVs
    try:
        students_df = pd.read_csv(students_csv_path)
        courses_df = pd.read_csv(courses_csv_path)
        rooms_df = pd.read_csv(rooms_csv_path)
    except Exception as e:
        raise ValueError(f"Error reading CSV files: {e}")
    
    # Normalize column names to lowercase
    students_df.columns = students_df.columns.str.lower()
    courses_df.columns = courses_df.columns.str.lower()
    rooms_df.columns = rooms_df.columns.str.lower()
    
    # Validate required columns
    required_student_cols = ['student_id', 'name', 'enrolled_courses']
    required_course_cols = ['course_id', 'code', 'name']
    required_room_cols = ['room_id', 'name', 'capacity']
    
    for col in required_student_cols:
        if col not in students_df.columns:
            raise ValueError(f"Missing required column in students CSV: {col}")
    
    for col in required_course_cols:
        if col not in courses_df.columns:
            raise ValueError(f"Missing required column in courses CSV: {col}")
    
    for col in required_room_cols:
        if col not in rooms_df.columns:
            raise ValueError(f"Missing required column in rooms CSV: {col}")
    
    # Debug: Print actual CSV data
    print("DEBUG: Students CSV data:")
    print(students_df.head())
    print(f"DEBUG: Student ID column type: {students_df['student_id'].dtype}")
    print(f"DEBUG: First few student IDs: {students_df['student_id'].head().tolist()}")
    print(f"DEBUG: All columns: {list(students_df.columns)}")
    print(f"DEBUG: CSV shape: {students_df.shape}")
    print("DEBUG: First 3 rows raw data:")
    for i in range(min(3, len(students_df))):
        row = students_df.iloc[i]
        print(f"Row {i}: {dict(row)}")
    
    # Parse enrollments from students' enrolled_courses column
    enrollments = []
    for _, student in students_df.iterrows():
        student_id = student['student_id']
        enrolled_courses = str(student['enrolled_courses'])
        print(f"DEBUG: Processing student_id={student_id}, enrolled_courses={enrolled_courses}")
        
        # Split by various separators
        course_codes = re.split(r'[,;|/\s]+', enrolled_courses)
        course_codes = [code.strip() for code in course_codes if code.strip()]
        
        for course_code in course_codes:
            # Find course_id from courses_df
            course_match = courses_df[courses_df['code'] == course_code]
            if not course_match.empty:
                course_id = course_match.iloc[0]['course_id']
                enrollments.append({'student_id': student_id, 'course_id': course_id})
    
    enrollments_df = pd.DataFrame(enrollments)
    
    return {
        'students': students_df,
        'courses': courses_df,
        'rooms': rooms_df,
        'enrollments': enrollments_df
    }

if __name__ == "__main__":
    # Demo with sample files from data/
    data_dir = "data"
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if len(csv_files) >= 3:
        students_file = next((f for f in csv_files if 'student' in f.lower()), csv_files[0])
        courses_file = next((f for f in csv_files if 'course' in f.lower()), csv_files[1])
        rooms_file = next((f for f in csv_files if 'room' in f.lower()), csv_files[2])
        
        try:
            result = parse_csvs(
                os.path.join(data_dir, students_file),
                os.path.join(data_dir, courses_file),
                os.path.join(data_dir, rooms_file)
            )
            
            print("Parsing successful!")
            print(f"Students: {len(result['students'])} rows")
            print(f"Courses: {len(result['courses'])} rows")
            print(f"Rooms: {len(result['rooms'])} rows")
            print(f"Enrollments: {len(result['enrollments'])} rows")
            
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Need at least 3 CSV files in data/ directory for demo")