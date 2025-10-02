import pandas as pd
import math

def allocate_rooms(timetable, rooms_df, config):
    """
    Allocate rooms to exams and assign seats with column-based interleaving.
    
    Args:
        timetable: List of exam assignments
        rooms_df: DataFrame with room information
        config: Configuration dictionary
    
    Returns:
        Updated timetable with room assignments and seat maps
    """
    updated_timetable = []
    
    # Group exams by time slot
    slot_groups = {}
    for exam in timetable:
        slot_key = f"{exam['slot_date']}_{exam['slot_time']}"
        if slot_key not in slot_groups:
            slot_groups[slot_key] = []
        slot_groups[slot_key].append(exam)
    
    for slot_key, exams in slot_groups.items():
        # Calculate total capacity needed for this slot
        total_students = sum(len(exam['assignments'][0]['students']) for exam in exams)
        total_capacity = rooms_df['capacity'].sum()
        
        # Mark as unschedulable if insufficient capacity
        if total_students > total_capacity:
            for exam in exams:
                exam['status'] = 'unschedulable'
                exam['reason'] = 'Insufficient room capacity'
                updated_timetable.append(exam)
            continue
        
        # Allocate rooms to exams
        available_rooms = rooms_df.copy().sort_values('capacity', ascending=False)
        
        for exam in exams:
            students = exam['assignments'][0]['students']
            students_needed = len(students)
            
            # Find rooms that can accommodate students
            allocated_rooms = []
            remaining_students = students[:]
            
            for _, room in available_rooms.iterrows():
                if not remaining_students:
                    break
                
                room_capacity = room['capacity']
                room_students = remaining_students[:room_capacity]
                remaining_students = remaining_students[room_capacity:]
                
                # Assign seats for this room
                seat_assignments = assign_seats_for_room(
                    room['room_id'], 
                    room_students, 
                    room.get('num_columns', 4)
                )
                
                allocated_rooms.append({
                    'room_id': room['room_id'],
                    'students': room_students,
                    'seat_assignments': seat_assignments
                })
            
            # Update exam with room allocations
            exam['assignments'] = allocated_rooms
            exam['status'] = 'scheduled' if not remaining_students else 'partial'
            
            if remaining_students:
                exam['unassigned_students'] = remaining_students
            
            updated_timetable.append(exam)
    
    return updated_timetable

def assign_seats_for_room(room_id, students_list, num_columns):
    """
    Assign seats using column-based interleaving to prevent side-by-side same-course students.
    
    Args:
        room_id: Room identifier
        students_list: List of student IDs
        num_columns: Number of columns in the room
    
    Returns:
        List of seat assignments with student_id, row, column
    """
    if not students_list:
        return []
    
    seat_assignments = []
    num_students = len(students_list)
    num_rows = math.ceil(num_students / num_columns)
    
    # Fill seats column by column to ensure interleaving
    student_idx = 0
    for col in range(num_columns):
        for row in range(num_rows):
            if student_idx < num_students:
                seat_assignments.append({
                    'student_id': students_list[student_idx],
                    'row': row + 1,  # 1-based indexing
                    'column': col + 1  # 1-based indexing
                })
                student_idx += 1
    
    return seat_assignments

if __name__ == "__main__":
    # Demo with sample data
    sample_timetable = [
        {
            'course_id': 'C001',
            'slot_date': '2024-05-01',
            'slot_time': '09:00-12:00',
            'assignments': [{
                'room_id': 'TBD',
                'students': ['S001', 'S002', 'S003', 'S004', 'S005']
            }]
        },
        {
            'course_id': 'C002',
            'slot_date': '2024-05-01',
            'slot_time': '09:00-12:00',
            'assignments': [{
                'room_id': 'TBD',
                'students': ['S006', 'S007', 'S008']
            }]
        }
    ]
    
    sample_rooms = pd.DataFrame([
        {'room_id': 'R001', 'name': 'Room A', 'capacity': 6, 'num_columns': 3},
        {'room_id': 'R002', 'name': 'Room B', 'capacity': 4, 'num_columns': 2}
    ])
    
    config = {'column_interleaving': True}
    
    result = allocate_rooms(sample_timetable, sample_rooms, config)
    
    print("Room allocation completed!")
    for exam in result:
        print(f"\nCourse {exam['course_id']} - Status: {exam.get('status', 'scheduled')}")
        for assignment in exam['assignments']:
            print(f"  Room {assignment['room_id']}: {len(assignment['students'])} students")
            print(f"  Seat map: {assignment['seat_assignments'][:3]}...")  # Show first 3 seats