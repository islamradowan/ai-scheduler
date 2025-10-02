# AI Exam Scheduler

Python-based exam scheduling system using genetic algorithms and constraint optimization to automatically generate conflict-free exam timetables with room allocation and seat assignments.

## Features
- **Genetic Algorithm Optimization**: Uses DEAP library for intelligent exam scheduling
- **Conflict Resolution**: Automatically detects and resolves student enrollment conflicts
- **Room Allocation**: Smart room assignment with capacity management
- **Seat Assignment**: Column-based interleaving to prevent cheating
- **Invigilator Assignment**: Automatic teacher allocation with availability constraints
- **Export Capabilities**: Generate Excel and PDF reports
- **Web Interface**: Simple upload and download interface
- **Makeup Scheduling**: Handles unschedulable exams with alternative slots

## Tech Stack
- **FastAPI**: Modern web framework for APIs
- **SQLAlchemy**: Database ORM for data persistence
- **Pandas**: Data manipulation and analysis
- **NetworkX**: Graph algorithms for conflict detection
- **DEAP**: Genetic algorithm optimization
- **OpenPyXL**: Excel file generation
- **ReportLab**: PDF report generation
- **Jinja2**: HTML templating

## Prerequisites
- Python 3.10 or higher
- pip package manager

## Setup Instructions

### 1. Clone and Navigate
```bash
cd aischeduler
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database
```bash
python -c "from app.database import create_db; create_db()"
```

### 5. Start Server
```bash
uvicorn app.main:app --reload --port 8000
```

The application will be available at: http://localhost:8000

## Usage

### Web Interface
1. Open http://localhost:8000 in your browser
2. Upload three CSV files:
   - **Students CSV**: student_id, name, batch_type, year, section, enrolled_courses
   - **Courses CSV**: course_id, code, name, semester, department, exam_type, priority_flag
   - **Rooms CSV**: room_id, name, capacity, num_columns
3. Configure scheduling parameters (optional)
4. Click "Generate Schedule"
5. Download Excel and PDF reports from results page

### API Endpoints
- `GET /health` - Health check
- `POST /upload` - Upload CSV files
- `POST /schedule` - Generate exam schedule
- `GET /schedule/status` - Check generation status

### CSV File Formats

#### Students CSV
```csv
student_id,name,batch_type,year,section,enrolled_courses
S001,Alice Smith,Regular,2023,A,MATH101;PHYS101;CHEM101
S002,Bob Johnson,Regular,2023,B,PHYS101,CHEM101
```

#### Courses CSV
```csv
course_id,code,name,semester,department,exam_type,priority_flag
C001,MATH101,Mathematics,1,Science,Final,true
C002,PHYS101,Physics,1,Science,Final,false
```

#### Rooms CSV
```csv
room_id,name,capacity,num_columns
R001,Main Hall,100,10
R002,Lab Room,30,5
```

## Configuration

Edit `app/config.yaml` to customize:
- Exam days and time slots
- Maximum exams per student per day
- Genetic algorithm parameters
- Room allocation rules

## Output Files

Generated files are saved to `outputs/`:
- `timetable.xlsx` - Complete schedule with multiple sheets
- `timetable.pdf` - Summary report with seat maps

## Development

### Run Tests
```bash
pytest -v
```

### VSCode Tasks
Use Ctrl+Shift+P → "Tasks: Run Task":
- Run FastAPI
- Run Tests
- Create Database

## Troubleshooting

### Common Issues

**"Module not found" errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**Database errors**
- Run database initialization: `python -c "from app.database import create_db; create_db()"`
- Check that `data/` directory exists

**CSV parsing errors**
- Verify CSV files have required columns
- Check for proper encoding (UTF-8)
- Ensure enrolled_courses uses supported separators: `,;|/ `

**Scheduling fails**
- Reduce population size or generations in config for faster testing
- Check for conflicting constraints (too many students, too few rooms)
- Verify exam days and slots are properly configured

**Port already in use**
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

**Permission errors on Windows**
- Run terminal as Administrator
- Check antivirus software isn't blocking file operations

### Performance Tips
- For large datasets (>1000 students), increase GA generations
- Use fewer exam days to reduce complexity
- Ensure adequate room capacity for all students

### Getting Help
- Check logs in terminal for detailed error messages
- Verify all CSV files are properly formatted
- Test with smaller datasets first

## Architecture

```
app/
├── main.py              # FastAPI application
├── config.yaml          # Configuration settings
├── database.py          # Database connection
├── models.py            # SQLAlchemy models
├── parser.py            # CSV parsing
├── conflict_graph.py    # Conflict detection
├── scheduler_core.py    # Genetic algorithm
├── room_allocator.py    # Room assignment
├── invigilator_assigner.py # Teacher assignment
├── conflict_handler.py  # Makeup scheduling
├── exporter.py          # File generation
└── routes/              # API endpoints
    ├── upload.py
    └── schedule.py
```