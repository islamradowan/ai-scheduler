import pandas as pd
from datetime import datetime, timedelta

def detect_unschedulable(timetable, rooms_df):
    """
    Detect unschedulable exams and provide reasons.
    
    Args:
        timetable: List of exam assignments
        rooms_df: DataFrame with room information
    
    Returns:
        List of unschedulable exams with reasons
    """
    unschedulable = []
    total_capacity = rooms_df['capacity'].sum()
    
    for exam in timetable:
        reasons = []
        
        # Check if marked as unschedulable
        if exam.get('status') == 'unschedulable':
            reasons.append(exam.get('reason', 'Unknown reason'))
        
        # Check for insufficient room capacity
        total_students = sum(len(assignment.get('students', [])) for assignment in exam.get('assignments', []))
        if total_students > total_capacity:
            reasons.append(f"Total students ({total_students}) exceed room capacity ({total_capacity})")
        
        # Check for unassigned students
        if 'unassigned_students' in exam:
            unassigned_count = len(exam['unassigned_students'])
            reasons.append(f"{unassigned_count} students could not be assigned to rooms")
        
        # Check for missing invigilators
        missing_invigilators = 0
        for assignment in exam.get('assignments', []):
            if not assignment.get('invigilator'):
                missing_invigilators += 1
        
        if missing_invigilators > 0:
            reasons.append(f"{missing_invigilators} rooms without invigilators")
        
        if reasons:
            unschedulable.append({
                'course_id': exam['course_id'],
                'slot_date': exam.get('slot_date'),
                'slot_time': exam.get('slot_time'),
                'reasons': reasons,
                'student_count': total_students
            })
    
    return unschedulable

def schedule_makeup(unschedulable_list, config, start_date):
    """
    Schedule makeup exams for unschedulable courses using greedy approach.
    
    Args:
        unschedulable_list: List of unschedulable exams
        config: Configuration dictionary
        start_date: Start date for makeup scheduling (string)
    
    Returns:
        List of makeup exam proposals
    """
    if not unschedulable_list:
        return []
    
    # Generate makeup slots starting from start_date
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    exam_slots = config.get('exam_slots', [{'start_time': '09:00', 'end_time': '12:00'}])
    buffer_days = config.get('buffer_days', 2)
    
    makeup_slots = []
    for day_offset in range(buffer_days, buffer_days + 7):  # 7 days of makeup slots
        makeup_date = start_dt + timedelta(days=day_offset)
        for slot in exam_slots:
            makeup_slots.append({
                'date': makeup_date.strftime('%Y-%m-%d'),
                'start_time': slot['start_time'],
                'end_time': slot['end_time']
            })
    
    # Greedy assignment of makeup exams
    makeup_schedule = []
    used_slots = set()
    
    # Sort by student count (larger exams first)
    sorted_exams = sorted(unschedulable_list, key=lambda x: x['student_count'], reverse=True)
    
    for exam in sorted_exams:
        assigned = False
        
        for i, slot in enumerate(makeup_slots):
            slot_key = f"{slot['date']}_{slot['start_time']}-{slot['end_time']}"
            
            if slot_key not in used_slots:
                makeup_schedule.append({
                    'course_id': exam['course_id'],
                    'original_reasons': exam['reasons'],
                    'makeup_date': slot['date'],
                    'makeup_time': f"{slot['start_time']}-{slot['end_time']}",
                    'student_count': exam['student_count'],
                    'status': 'proposed'
                })
                used_slots.add(slot_key)
                assigned = True
                break
        
        if not assigned:
            makeup_schedule.append({
                'course_id': exam['course_id'],
                'original_reasons': exam['reasons'],
                'makeup_date': None,
                'makeup_time': None,
                'student_count': exam['student_count'],
                'status': 'no_slot_available'
            })
    
    return makeup_schedule

if __name__ == "__main__":
    # Demo with sample data
    sample_timetable = [
        {
            'course_id': 'C001',
            'slot_date': '2024-05-01',
            'slot_time': '09:00-12:00',
            'status': 'scheduled',
            'assignments': [
                {'room_id': 'R001', 'students': ['S001', 'S002'], 'invigilator': 'T001'}
            ]
        },
        {
            'course_id': 'C002',
            'slot_date': '2024-05-01',
            'slot_time': '09:00-12:00',
            'status': 'unschedulable',
            'reason': 'Insufficient room capacity',
            'assignments': [
                {'room_id': 'R001', 'students': ['S003', 'S004', 'S005'], 'invigilator': None}
            ]
        },
        {
            'course_id': 'C003',
            'slot_date': '2024-05-01',
            'slot_time': '14:00-17:00',
            'assignments': [
                {'room_id': 'R002', 'students': ['S006'], 'invigilator': None}
            ],
            'unassigned_students': ['S007', 'S008']
        }
    ]
    
    sample_rooms = pd.DataFrame([
        {'room_id': 'R001', 'capacity': 2},
        {'room_id': 'R002', 'capacity': 1}
    ])
    
    config = {
        'exam_slots': [
            {'start_time': '09:00', 'end_time': '12:00'},
            {'start_time': '14:00', 'end_time': '17:00'}
        ],
        'buffer_days': 2
    }
    
    # Detect unschedulable exams
    unschedulable = detect_unschedulable(sample_timetable, sample_rooms)
    print("Unschedulable exams detected:")
    for exam in unschedulable:
        print(f"  Course {exam['course_id']}: {exam['reasons']}")
    
    # Schedule makeup exams
    makeup_schedule = schedule_makeup(unschedulable, config, '2024-05-01')
    print(f"\nMakeup schedule ({len(makeup_schedule)} exams):")
    for makeup in makeup_schedule:
        if makeup['makeup_date']:
            print(f"  Course {makeup['course_id']}: {makeup['makeup_date']} {makeup['makeup_time']}")
        else:
            print(f"  Course {makeup['course_id']}: No slot available")