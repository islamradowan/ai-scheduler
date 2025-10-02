# AI Exam Scheduler — Task List (Python-only, FastAPI)

Follow prompts in order (PROMPT-01 → PROMPT-20) using Amazon Q in VSCode. Paste one prompt at a time, generate files, run acceptance checks, then continue.

## Setup & scaffolding
- [x] 00. Repo init & skeleton
  - Acceptance: repo contains `app/`, `data/`, `outputs/`, `tests/`, `requirements.txt`, `.vscode/`.
  - Prompt: PROMPT-00-REPO_SCAFFOLD

- [x] 01. FastAPI app skeleton
  - Files: `app/main.py`, `app/__init__.py`, `app/config.yaml`, `requirements.txt`
  - Acceptance: `uvicorn app.main:app --reload` exposes `/health` returning 200 JSON.
  - Prompt: PROMPT-01-FASTAPI_SCAFFOLD

## Persistence & models
- [x] 02. Database + models
  - Files: `app/database.py`, `app/models.py`, `app/crud.py`
  - Acceptance: `python -c "from app.database import create_db; create_db()"` creates SQLite DB file and tables.
  - Prompt: PROMPT-02-MODELS_DB

## File input & parsing
- [x] 03. CSV upload endpoint
  - Files: `app/routes/upload.py` and registration in `main.py`
  - Acceptance: POST `/upload` stores CSVs to `data/` and returns stored paths.
  - Prompt: PROMPT-03-UPLOAD

- [x] 04. Parser
  - Files: `app/parser.py`
  - Acceptance: `python -c "from app.parser import parse_csvs; parse_csvs('data/student.csv','data/course.csv','data/room.csv')"` returns DataFrames and a normalized enrollments table.
  - Prompt: PROMPT-04-PARSER

## Core scheduling components
- [x] 05. Conflict graph
  - Files: `app/conflict_graph.py`
  - Acceptance: `python -c "from app.conflict_graph import build_conflict_graph; print(build_conflict_graph(...))"` returns graph stats.
  - Prompt: PROMPT-05-CONFLICT_GRAPH

- [x] 06. Scheduler core (Genetic Algorithm)
  - Files: `app/scheduler_core.py`
  - Acceptance: `python -c "from app.scheduler_core import schedule; schedule(...)"` returns timetable JSON and score for a small sample dataset.
  - Prompt: PROMPT-06-SCHEDULER_CORE

- [x] 07. Room allocator & seat assignment
  - Files: `app/room_allocator.py`
  - Acceptance: seat maps respect column-interleaving and no side-by-side same-course students.
  - Prompt: PROMPT-07-ROOM_ALLOCATOR

- [x] 08. Invigilator assigner
  - Files: `app/invigilator_assigner.py`
  - Acceptance: teachers assigned respecting availability and max_rooms_per_teacher.
  - Prompt: PROMPT-08-INVIG_ASSIGNER

- [x] 09. Conflict handler & makeup scheduler
  - Files: `app/conflict_handler.py`
  - Acceptance: unschedulable exams are detected and makeup slots proposed.
  - Prompt: PROMPT-09-CONFLICT_HANDLER

- [x] 10. Exporter (Excel + PDF)
  - Files: `app/exporter.py`
  - Acceptance: `exporter.export_excel(timetable,'outputs/timetable.xlsx')` and `export_pdf('outputs/timetable.pdf')` produce files.
  - Prompt: PROMPT-10-EXPORTER

## Integration & UI
- [x] 11. `/schedule` API route (pipeline orchestration)
  - Files: `app/routes/schedule.py` and registration
  - Acceptance: POST `/schedule` runs end-to-end pipeline and returns links to generated files.
  - Prompt: PROMPT-11-SCHEDULE_ROUTE

- [x] 12. Minimal web UI (Jinja2)
  - Files: `app/templates/upload.html`, `app/templates/results.html`
  - Acceptance: Browser UI to upload CSVs and show download links for results.
  - Prompt: PROMPT-12-TEMPLATES_UI

## Tests, tasks & documentation
- [x] 13. Unit & integration tests
  - Files: `tests/test_parser.py`, `tests/test_conflict_graph.py`, `tests/test_scheduler.py`
  - Acceptance: `pytest -q` returns passing basic tests.
  - Prompt: PROMPT-13-TESTS

- [x] 14. VSCode tasks
  - Files: `.vscode/tasks.json`
  - Acceptance: VSCode shows tasks: Run FastAPI, Run tests.
  - Prompt: PROMPT-14-VSCODE_TASKS

- [x] 15. README & runbook
  - Files: `README.md` with setup instructions for Windows/Linux/macOS and sample dataset usage.
  - Acceptance: README includes `pip install -r requirements.txt`, run server, run schedule step.
  - Prompt: PROMPT-15-README

## Optional / polish
- [x] 16. Sample dataset + seed script (small subset)
  - Files: `data/sample_student.csv`, `data/sample_course.csv`, `data/sample_room.csv`, `scripts/seed_sample.py`
  - Acceptance: Seed script inserts sample rows to DB for quick testing.
  - Prompt: PROMPT-16-SAMPLE_DATA
