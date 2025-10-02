AI-Powered Exam Scheduler – Final Project Specification (Dataset-Aware)

1. Project Overview
The AI-Powered Exam Scheduler generates conflict-free, optimized exam timetables for engineering faculties in Bangladeshi universities.
Dataset-driven adjustments include:

Real room sizes (room.csv)

Real course load and priorities (course.csv)

Real student enrollments (student.csv)

2. Key Features (Dataset-Tuned)

Supports Midterm (1.5h) and Final (2h) exams.

Dynamic scheduling tuned to actual batch distributions from student dataset.

Room splitting auto-triggered where enrollment > room capacity (seen in dataset).

Priority courses auto-marked (final-year courses from dataset + manual overrides).

Seat maps generated column-wise (actual num_columns from room.csv).

Invigilator assignment balanced across available teachers.

Holiday avoidance (via holidays.csv).

Excel + PDF outputs with exam timetables, seat maps, and invigilator rosters.

3. Rules and Constraints (Dataset Specific)

Fixed Rules

Max 1 exam/student/day.

Seat arrangement: column-based, no side-by-side for same course.

Room capacity strictly enforced.

Dynamic Rules (Configurable via YAML)

Rule	Default	Dynamic Option
Max global exams/day	2	Adjust via config
Exam days/week	5 (Sat, Sun, Tue, Wed, Fri)	Evening/Regular batch rules from dataset
Buffer days	Regular = 1	Configurable; Evening = 0
Priority courses	Final-year	Manual overrides allowed
Public holidays	From CSV	Auto-avoid those dates

4. Input Data (from dataset)

Students (student.csv): student_id, name, batch_type, year, section, enrolled_courses

Courses (course.csv): course_id, code, name, semester, department, exam_type, priority_flag

Rooms (room.csv): room_id, name, capacity, num_columns

Invigilators (manual CSV): teacher_id, name, availability

Config (ai_exam_scheduler_config.yaml): dynamic rules, holidays

5. Output Data

Timetable (date, slot, room)

Room & seat assignments (column-based maps)

Invigilator assignments

Conflict exceptions + makeup schedule

Benchmark reports (fairness, utilization, conflicts avoided)

Formats: Excel + PDF

6. Scheduling & Optimization Logic (Dataset-aware)

Load dataset (students, courses, rooms) + config.

Build conflict graph (shared students → edge between courses).

Assign slots respecting student, batch, and global rules.

Optimize fairness & conflict minimization with Genetic Algorithm.

Allocate rooms (split if course size > largest room capacity).

Generate seat maps (num_columns used for column interleaving).

Assign invigilators (availability + load balance).

Handle conflict exceptions → makeup schedule.

Export results (Excel/PDF).

7. System Architecture

Input Parser (CSV → DataFrames)

Conflict Graph Generator

Scheduler Engine (rules + optimization)

Room & Seat Allocator

Invigilator Assigner

Conflict Handler

Output Generator (Excel, PDF)

Benchmark Module

8. Database Schema (Dataset-Aware)

students → derived from student.csv

courses → derived from course.csv

rooms → derived from room.csv

enrollments → joined from student.csv + course.csv

timeslots → generated

exam_assignments, exam_rooms, seat_assignments, invigilator_assignments

9. Contributions

Dataset-specific exam scheduling

Configurable dynamic rules via YAML

Seat allocation with real column layouts from dataset

Conflict resolution + makeup handling

AI optimization with fairness metrics

PDF + Excel outputs for admin usability

10. Future Work

LMS/ERP integration

ML-based conflict prediction

Adaptive scheduling for absences/unavailability

More fairness dimensions (student workload, teacher load)