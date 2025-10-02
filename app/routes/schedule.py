from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import yaml
import os

from app.parser import parse_csvs
from app.conflict_graph import build_conflict_graph, graph_stats
from app.scheduler_core import schedule
from app.room_allocator import allocate_rooms
from app.invigilator_assigner import assign_invigilators
from app.conflict_handler import detect_unschedulable, schedule_makeup
from app.exporter import export_excel, export_pdf

router = APIRouter()

class ScheduleRequest(BaseModel):
    students_csv_path: str
    courses_csv_path: str
    rooms_csv_path: str
    exam_start_date: Optional[str] = None
    exam_end_date: Optional[str] = None
    exam_time_slots: Optional[list] = None
    max_global_exams_per_day: Optional[int] = None
    buffer_days: Optional[int] = None

@router.post("/schedule")
async def run_schedule_pipeline(request: ScheduleRequest):
    """
    Execute the complete scheduling pipeline.
    
    Returns JSON with status, score, and file paths.
    """
    try:
        # Load configuration
        config_path = "app/config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Apply overrides from request
        if request.exam_start_date and request.exam_end_date:
            # Generate exam days from start and end dates
            from datetime import datetime, timedelta
            start_date = datetime.strptime(request.exam_start_date, '%Y-%m-%d')
            end_date = datetime.strptime(request.exam_end_date, '%Y-%m-%d')
            
            exam_days = []
            current_date = start_date
            while current_date <= end_date:
                exam_days.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)
            
            config['exam_days'] = exam_days
        
        if request.exam_time_slots:
            # Use custom time slots from request
            config['exam_slots'] = request.exam_time_slots
        
        if request.max_global_exams_per_day:
            config['max_global_exams_per_day'] = request.max_global_exams_per_day
        if request.buffer_days:
            config['buffer_days'] = request.buffer_days
        
        # Step 1: Parse CSVs
        parsed_data = parse_csvs(
            request.students_csv_path,
            request.courses_csv_path,
            request.rooms_csv_path
        )
        
        students_df = parsed_data['students']
        courses_df = parsed_data['courses']
        rooms_df = parsed_data['rooms']
        enrollments_df = parsed_data['enrollments']
        
        # Step 2: Build conflict graph
        conflict_graph = build_conflict_graph(enrollments_df)
        graph_statistics = graph_stats(conflict_graph)
        
        # Step 3: Schedule exams using GA
        schedule_result = schedule(courses_df, students_df, rooms_df, enrollments_df, config)
        timetable = schedule_result['timetable']
        score = schedule_result['score']
        
        # Step 4: Allocate rooms and assign seats
        timetable = allocate_rooms(timetable, rooms_df, config)
        
        # Step 5: Assign invigilators (create dummy invigilators if none exist)
        import pandas as pd
        invigilators_df = pd.DataFrame([
            {
                'teacher_id': f'T{i:03d}',
                'name': f'Teacher {i}',
                'availability': []  # Available for all slots
            }
            for i in range(1, 11)  # Create 10 dummy teachers
        ])
        
        timetable = assign_invigilators(timetable, invigilators_df, config)
        
        # Step 6: Detect unschedulable exams
        unschedulable = detect_unschedulable(timetable, rooms_df)
        
        # Step 7: Schedule makeup exams if needed
        makeup_schedule = []
        if unschedulable:
            exam_days = config.get('exam_days', ['2024-05-01'])
            start_date = exam_days[0] if exam_days else '2024-05-01'
            makeup_schedule = schedule_makeup(unschedulable, config, start_date)
        
        # Step 8: Export files
        excel_path = "outputs/timetable.xlsx"
        pdf_path = "outputs/timetable.pdf"
        
        export_excel(timetable, excel_path)
        export_pdf(timetable, pdf_path, students_df)
        
        # Prepare response
        response = {
            "status": "success",
            "score": score,
            "statistics": {
                "total_courses": len(courses_df),
                "total_students": len(students_df),
                "total_enrollments": len(enrollments_df),
                "conflict_graph": graph_statistics,
                "scheduled_exams": len([e for e in timetable if e.get('status') != 'unschedulable']),
                "unschedulable_exams": len(unschedulable),
                "makeup_exams": len(makeup_schedule)
            },
            "files": {
                "excel": excel_path,
                "pdf": pdf_path
            },
            "unschedulable": unschedulable,
            "makeup_schedule": makeup_schedule
        }
        
        return response
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Data validation error: {str(e)}")
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Schedule error: {str(e)}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/schedule/status")
async def get_schedule_status():
    """Get current scheduling status and available files."""
    excel_exists = os.path.exists("outputs/timetable.xlsx")
    pdf_exists = os.path.exists("outputs/timetable.pdf")
    
    return {
        "files_available": {
            "excel": excel_exists,
            "pdf": pdf_exists
        },
        "last_generated": "N/A"  # Could be enhanced to track timestamps
    }