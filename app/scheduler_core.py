import random
import pandas as pd
from deap import base, creator, tools, algorithms
from collections import defaultdict
import yaml

def schedule(courses_df, students_df, rooms_df, enrollments_df, config):
    """
    Schedule exams using genetic algorithm.
    
    Returns:
        dict: {timetable: [...], score: float}
    """
    
    # Load config defaults
    pop_size = config.get('optimization', {}).get('population_size', 50)
    generations = config.get('optimization', {}).get('generations', 100)
    
    # Create time slots from config
    exam_days = config.get('exam_days', ['2024-05-01', '2024-05-02'])
    exam_slots = config.get('exam_slots', [{'start_time': '09:00', 'end_time': '12:00'}])
    
    time_slots = []
    for day in exam_days:
        for slot in exam_slots:
            time_slots.append({
                'date': day,
                'start_time': slot['start_time'],
                'end_time': slot['end_time']
            })
    
    courses = courses_df['course_id'].tolist()
    n_courses = len(courses)
    n_slots = len(time_slots)
    
    # Student-course mapping
    student_courses = enrollments_df.groupby('student_id')['course_id'].apply(list).to_dict()
    
    # Setup DEAP - avoid recreating classes
    if not hasattr(creator, "FitnessMax"):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    if not hasattr(creator, "Individual"):
        creator.create("Individual", list, fitness=creator.FitnessMax)
    
    toolbox = base.Toolbox()
    toolbox.register("attr_int", random.randint, 0, n_slots - 1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_int, n_courses)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    
    def evaluate(individual):
        # Map courses to slots
        course_to_slot = {courses[i]: individual[i] for i in range(n_courses)}
        
        penalty = 0
        
        # Hard constraint: max 1 exam per student per day
        for student_id, student_course_list in student_courses.items():
            day_exams = defaultdict(int)
            for course_id in student_course_list:
                slot_idx = course_to_slot[course_id]
                day = time_slots[slot_idx]['date']
                day_exams[day] += 1
            
            for day, count in day_exams.items():
                if count > 1:
                    penalty += (count - 1) * 1000  # Heavy penalty
        
        # Soft penalty: room splits (simplified - assume need room splits if >50 students)
        room_split_penalty = 0
        for course_id in courses:
            course_students = len(enrollments_df[enrollments_df['course_id'] == course_id])
            if course_students > 50:  # Simplified threshold
                room_split_penalty += 10
        
        penalty += room_split_penalty
        
        return (1000 - penalty,)  # Higher is better
    
    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutUniformInt, low=0, up=n_slots-1, indpb=0.1)
    toolbox.register("select", tools.selTournament, tournsize=3)
    
    # Run GA
    pop = toolbox.population(n=pop_size)
    hof = tools.HallOfFame(1)
    
    algorithms.eaSimple(pop, toolbox, cxpb=0.8, mutpb=0.1, ngen=generations, 
                       halloffame=hof, verbose=False)
    
    # Build timetable from best solution
    best_individual = hof[0]
    course_to_slot = {courses[i]: best_individual[i] for i in range(n_courses)}
    
    timetable = []
    for course_id, slot_idx in course_to_slot.items():
        slot = time_slots[slot_idx]
        course_students = enrollments_df[enrollments_df['course_id'] == course_id]['student_id'].tolist()
        
        # Get course details
        course_info = courses_df[courses_df['course_id'] == course_id].iloc[0]
        
        timetable.append({
            'course_id': course_id,
            'course_code': course_info.get('code', ''),
            'course_name': course_info.get('name', ''),
            'slot_date': slot['date'],
            'slot_time': f"{slot['start_time']}-{slot['end_time']}",
            'assignments': [{
                'room_id': 'TBD',  # Will be assigned by room allocator
                'students': course_students
            }]
        })
    
    score = best_individual.fitness.values[0]
    
    return {
        'timetable': timetable,
        'score': score
    }

if __name__ == "__main__":
    # Demo with sample data
    sample_courses = pd.DataFrame([
        {'course_id': 'C001', 'code': 'MATH101', 'name': 'Mathematics'},
        {'course_id': 'C002', 'code': 'PHYS101', 'name': 'Physics'},
        {'course_id': 'C003', 'code': 'CHEM101', 'name': 'Chemistry'}
    ])
    
    sample_students = pd.DataFrame([
        {'student_id': 'S001', 'name': 'Alice'},
        {'student_id': 'S002', 'name': 'Bob'},
        {'student_id': 'S003', 'name': 'Charlie'},
        {'student_id': 'S004', 'name': 'Diana'},
        {'student_id': 'S005', 'name': 'Eve'}
    ])
    
    sample_enrollments = pd.DataFrame([
        {'student_id': 'S001', 'course_id': 'C001'},
        {'student_id': 'S001', 'course_id': 'C002'},
        {'student_id': 'S002', 'course_id': 'C002'},
        {'student_id': 'S002', 'course_id': 'C003'},
        {'student_id': 'S003', 'course_id': 'C001'},
        {'student_id': 'S004', 'course_id': 'C003'},
        {'student_id': 'S005', 'course_id': 'C001'}
    ])
    
    sample_rooms = pd.DataFrame([
        {'room_id': 'R001', 'name': 'Room A', 'capacity': 30}
    ])
    
    config = {
        'exam_days': ['2024-05-01', '2024-05-02'],
        'exam_slots': [
            {'start_time': '09:00', 'end_time': '12:00'},
            {'start_time': '14:00', 'end_time': '17:00'}
        ],
        'optimization': {
            'population_size': 20,
            'generations': 10
        }
    }
    
    result = schedule(sample_courses, sample_students, sample_rooms, sample_enrollments, config)
    
    print("Scheduling completed!")
    print(f"Score: {result['score']}")
    print(f"Number of scheduled exams: {len(result['timetable'])}")
    
    for exam in result['timetable']:
        print(f"Course {exam['course_id']}: {exam['slot_date']} {exam['slot_time']} - {len(exam['assignments'][0]['students'])} students")