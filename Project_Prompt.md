Instruction for each prompt: Paste the entire prompt text below into Amazon Q. Ask it to generate the specified files. Require: the assistant must return file path + file content in code blocks only (no extra explanation). After each generation run the acceptance commands from PROJECT_TASKS.md


PROMPT ID: PROMPT-00-REPO_SCAFFOLD

You are an expert Python full-stack engineer. Create repository scaffolding files for the "AI Exam Scheduler" Python project.

Tasks (create files only; respond with file path + contents in code blocks, no extra explanation):
- README.md (short intro, tech stack, quickstart)
- .gitignore (Python, VSCode, env)
- requirements.txt placeholder (leave comment that later prompts will append libs)
- Create folders: app/, app/templates/, data/, outputs/, tests/, scripts/, .vscode/
- Create empty placeholder files: app/__init__.py, app/main.py (simple health endpoint), app/config.yaml (leave placeholder), data/.gitkeep, outputs/.gitkeep, tests/.gitkeep, scripts/.gitkeep

Acceptance: Files present in the response. Do not run any commands.

PROMPT ID: PROMPT-01-FASTAPI_SCAFFOLD

You are an expert FastAPI developer. Create a minimal FastAPI app skeleton.

Files to produce (return path + contents only):
- app/main.py: FastAPI app, mount templates, route GET /health returns {"status":"ok"}, include routers registration placeholders.
- app/config.yaml: include the tuned YAML config for the project (global rules, room rules, optimization defaults). Use the YAML we discussed (max_exams_per_student_per_day:1, default exam days, buffer days, optimization GA defaults).
- requirements.txt: add base libs: fastapi, uvicorn, sqlalchemy, pandas, networkx, deap, ortools, openpyxl, reportlab, jinja2, pydantic
- .env.example: show DB path (sqlite:///./data/scheduler.db) and server port.

Acceptance: Running `uvicorn app.main:app --reload` exposes GET /health that returns 200 JSON {"status":"ok"}.

PROMPT ID: PROMPT-02-MODELS_DB

You are a Python backend dev. Create SQLAlchemy models and DB helper code.

Files (return path + contents only):
- app/database.py: SQLAlchemy engine for SQLite, `get_session()` dependency, `create_db()` function to create all tables.
- app/models.py: SQLAlchemy models (declarative) for tables:
  - Student (student_id PK text), name, batch_type, year, section
  - Course (id PK int autoinc), code, name, semester int, department, exam_type, priority_flag boolean
  - Enrollment (id, student_id FK, course_id FK)
  - Room (room_id PK text, name, capacity int, num_columns int)
  - Timeslot (id, date, start_time, end_time)
  - ExamAssignment (id, course_id FK, slot_id FK)
  - ExamRoom (id, exam_assignment_id FK, room_id FK)
  - SeatAssignment (id, exam_assignment_id FK, room_id FK, student_id FK, row int, column int)
  - Invigilator (teacher_id PK text, name, availability JSON)
  - InvigilatorAssignment (id, exam_assignment_id, room_id, teacher_id, load_balance_score)
- app/crud.py: simple helper functions for create/get for students, courses, enrollments, rooms.

Acceptance: `python -c "from app.database import create_db; create_db()"` creates SQLite file and tables.

PROMPT ID: PROMPT-03-UPLOAD

You are a FastAPI developer. Implement CSV upload endpoint and save to data/.

Files (path + content only):
- app/routes/upload.py: router with POST /upload accepting multipart files 'students','courses','rooms'. Validate extensions, save files to data/ with unique names, return JSON {"status":"ok","paths":{...}}.
- Update app/main.py to include router import and registration (if placeholder present).

Acceptance: POST to /upload with three CSVs returns JSON with saved paths and the files appear under data/.

PROMPT ID: PROMPT-04-PARSER

You are a Python data engineer. Implement parser to normalize CSVs.

File:
- app/parser.py: implement function parse_csvs(students_csv_path, courses_csv_path, rooms_csv_path) -> dict containing pandas DataFrames: students, courses, rooms, enrollments (table rows: student_id, course_id).
  - Parse `students` enrolled column supporting separators [, ; | / space].
  - Normalize column names to lower-case.
  - If missing required columns, raise ValueError with explicit message.

Include a short CLI demo block under `if __name__ == "__main__":` that loads files from data/ and prints basic stats.

Return file only.

PROMPT ID: PROMPT-05-CONFLICT_GRAPH

You are a Python algorithm engineer. Implement conflict graph utilities.

File:
- app/conflict_graph.py:
  - function build_conflict_graph(enrollments_df) -> networkx.Graph (nodes=course_code or id, edges between courses sharing ≥1 student).
  - function graph_stats(G) -> dict {n_nodes, n_edges, density, avg_degree, max_degree_course}
  - Include docstrings and a small demo under __main__.

Return file only.

PROMPT ID: PROMPT-06-SCHEDULER_CORE

You are an optimization engineer. Create GA-based scheduler core.

File:
- app/scheduler_core.py with:
  - function schedule(courses_df, students_df, rooms_df, enrollments_df, config) -> dict with keys:
    - timetable: list of {course_id, slot_date, slot_time, assignments: [{room_id, students: [student_ids]}]}
    - score: float
  - Use DEAP for GA, with a chromosome mapping course->slot index. Include fitness combining:
    - Hard penalty for any student >1 exam/day.
    - Soft penalty for number of room splits, fairness variance across students.
  - Provide minimal working GA parameters (pop size = config or 50, gens = config or 100).
  - Include `if __name__ == "__main__":` demo using sample CSVs in data/ and print summary.

Return file only.

PROMPT ID: PROMPT-07-ROOM_ALLOCATOR

You are a Python systems engineer. Implement room splitting & seat assignment.

File:
- app/room_allocator.py:
  - function allocate_rooms(timetable, rooms_df, config) -> updated timetable with room assignments and split info.
  - function assign_seats_for_room(room_id, students_list, num_columns) -> returns list of seat dicts {student_id,row,column} enforcing column-based interleaving so there are no side-by-side same-course students.
  - Mark exams as unschedulable if total students > sum of all rooms capacities for that slot.

Return file only.

PROMPT ID: PROMPT-08-INVIG_ASSIGNER

You are a Python dev. Implement invigilator assignment.

File:
- app/invigilator_assigner.py:
  - function assign_invigilators(timetable, invigilators_df, config) -> assigns teacher ids to each room per slot, respects teacher availability JSON (list of allowed dates/slots) and max_rooms_per_teacher.
  - Add warnings to timetable metadata if insufficient invigilators.

Return file only.

PROMPT ID: PROMPT-09-CONFLICT_HANDLER

You are a scheduling specialist. Implement conflict handler.

File:
- app/conflict_handler.py:
  - function detect_unschedulable(timetable, rooms_df) -> list of unschedulable exams with reasons.
  - function schedule_makeup(unschedulable_list, config, start_date) -> returns makeup timetable proposals (greedy planner).
  - Provide docstrings and a small example.

Return file only.

PROMPT ID: PROMPT-10-EXPORTER

You are a Python export specialist. Implement Excel & PDF export.

File:
- app/exporter.py:
  - function export_excel(timetable, out_path) -> uses openpyxl to create workbook with sheets: Timetable, Rooms, SeatMaps, Invigilators.
  - function export_pdf(timetable, out_path) -> basic PDF using reportlab or weasyprint with one-page summary and per-room seat maps (simple table).
  - Ensure generated files are saved to outputs/.

Return file only.

PROMPT ID: PROMPT-11-SCHEDULE_ROUTE

You are a FastAPI integrator. Create pipeline orchestration route.

File:
- app/routes/schedule.py:
  - POST /schedule accepts JSON or form with paths to student/course/room CSVs and optional overrides (max_global_exams_per_day, buffer_days).
  - Executes pipeline synchronously for dev:
    parse_csvs -> build_conflict_graph -> schedule -> allocate_rooms -> assign_invigilators -> detect_unschedulable -> schedule_makeup(if needed) -> export files.
  - Returns JSON with status, score, and file paths to outputs/timetable.xlsx and outputs/timetable.pdf

Add router registration in app/main.py if necessary.

Acceptance: POST to /schedule returns 200 and files exist in outputs/.

PROMPT ID: PROMPT-12-TEMPLATES_UI

You are a web UI dev (Jinja2). Create two minimal templates and static CSS.

Files:
- app/templates/upload.html: form to upload 3 CSVs and button to POST to /upload, and button to trigger /schedule.
- app/templates/results.html: displays schedule summary (JSON table) and links to download Excel/PDF.
- app/static/style.css: minimal styles.

Return files only.

PROMPT ID: PROMPT-13-TESTS

You are a test engineer. Add basic tests.

Files:
- tests/test_parser.py: tests parse_csvs with small inline DataFrames (or sample CSVs) asserting expected columns & enrollments table.
- tests/test_conflict_graph.py: creates small enrollments then assert graph nodes/edges.
- tests/test_scheduler.py: run scheduler_core.schedule on tiny dataset (3 courses, 5 students) and assert timetable is returned and no student has >1 exam/day.

Return tests only.

PROMPT ID: PROMPT-14-VSCODE_TASKS

You are a devops engineer. Return .vscode/tasks.json with tasks:
- Run FastAPI (uvicorn app.main:app)
- Run tests (pytest)
Return file only.

PROMPT ID: PROMPT-15-README

You are a technical writer. Produce README.md at repo root with:
- Project overview
- Prereqs (Python 3.10+)
- Setup steps:
  - python -m venv .venv
  - pip install -r requirements.txt
  - python -c "from app.database import create_db; create_db()"
  - uvicorn app.main:app --reload --port 8000
- How to upload CSVs, how to call /schedule, where outputs land (outputs/)
- Troubleshooting section
Return file only.

PROMPT ID: PROMPT-16-SAMPLE_DATA

You are a dataset engineer. quick local testing:

Files (in data/):
- Dataset/student.csv (student_id,name,batch_type,year,section,enrolled_courses)
- Dataset/course.csv (course_id,code,name,semester,department,exam_type,priority_flag)
- Dataset/room.csv (room_id,name,capacity,num_columns)

create scripts/seed_sample.py that reads dataset CSVs and inserts into DB via app/crud.py

Return files only.

