import pandas as pd
from collections import defaultdict

def assign_invigilators(timetable, invigilators_df, config):
    """
    Assign invigilators to exam rooms respecting availability and load limits.
    
    Args:
        timetable: List of exam assignments with room allocations
        invigilators_df: DataFrame with teacher information and availability
        config: Configuration with max_rooms_per_teacher
    
    Returns:
        Updated timetable with invigilator assignments and warnings
    """
    max_rooms_per_teacher = config.get('max_rooms_per_teacher', 3)
    updated_timetable = []
    warnings = []
    
    # Track teacher assignments per slot
    teacher_assignments = defaultdict(lambda: defaultdict(int))  # {slot: {teacher_id: room_count}}
    
    for exam in timetable:
        slot_key = f"{exam['slot_date']}_{exam['slot_time']}"
        
        for assignment in exam['assignments']:
            room_id = assignment['room_id']
            
            # Find available teacher for this slot
            assigned_teacher = None
            
            for _, teacher in invigilators_df.iterrows():
                teacher_id = teacher['teacher_id']
                availability = teacher.get('availability', [])
                
                # Check if teacher is available for this slot
                is_available = True
                if availability:  # If availability is specified, check it
                    slot_available = any(
                        slot.get('date') == exam['slot_date'] and 
                        slot.get('time') == exam['slot_time']
                        for slot in availability
                    )
                    if not slot_available:
                        is_available = False
                
                # Check if teacher hasn't exceeded room limit
                current_rooms = teacher_assignments[slot_key][teacher_id]
                if current_rooms >= max_rooms_per_teacher:
                    is_available = False
                
                if is_available:
                    assigned_teacher = teacher_id
                    teacher_assignments[slot_key][teacher_id] += 1
                    break
            
            # Assign teacher or add warning
            if assigned_teacher:
                assignment['invigilator'] = assigned_teacher
                assignment['load_balance_score'] = teacher_assignments[slot_key][assigned_teacher]
            else:
                assignment['invigilator'] = None
                warnings.append(f"No available invigilator for room {room_id} in slot {slot_key}")
        
        updated_timetable.append(exam)
    
    # Add warnings to timetable metadata
    if warnings:
        for exam in updated_timetable:
            if 'metadata' not in exam:
                exam['metadata'] = {}
            exam['metadata']['invigilator_warnings'] = warnings
    
    return updated_timetable

if __name__ == "__main__":
    # Demo with sample data
    sample_timetable = [
        {
            'course_id': 'C001',
            'slot_date': '2024-05-01',
            'slot_time': '09:00-12:00',
            'assignments': [
                {
                    'room_id': 'R001',
                    'students': ['S001', 'S002', 'S003']
                },
                {
                    'room_id': 'R002',
                    'students': ['S004', 'S005']
                }
            ]
        },
        {
            'course_id': 'C002',
            'slot_date': '2024-05-01',
            'slot_time': '14:00-17:00',
            'assignments': [
                {
                    'room_id': 'R001',
                    'students': ['S006', 'S007']
                }
            ]
        }
    ]
    
    sample_invigilators = pd.DataFrame([
        {
            'teacher_id': 'T001',
            'name': 'Dr. Smith',
            'availability': [
                {'date': '2024-05-01', 'time': '09:00-12:00'},
                {'date': '2024-05-01', 'time': '14:00-17:00'}
            ]
        },
        {
            'teacher_id': 'T002',
            'name': 'Prof. Johnson',
            'availability': [
                {'date': '2024-05-01', 'time': '09:00-12:00'}
            ]
        }
    ])
    
    config = {'max_rooms_per_teacher': 2}
    
    result = assign_invigilators(sample_timetable, sample_invigilators, config)
    
    print("Invigilator assignment completed!")
    for exam in result:
        print(f"\nCourse {exam['course_id']} - {exam['slot_date']} {exam['slot_time']}")
        for assignment in exam['assignments']:
            invigilator = assignment.get('invigilator', 'UNASSIGNED')
            print(f"  Room {assignment['room_id']}: {invigilator}")
        
        if 'metadata' in exam and 'invigilator_warnings' in exam['metadata']:
            print(f"  Warnings: {len(exam['metadata']['invigilator_warnings'])}")