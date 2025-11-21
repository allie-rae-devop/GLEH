# Post-Refactoring Guide

## New Project Structure

The project has been reorganized for clarity, maintainability, and future cloud migration:

```
HTML5 Project for courses/
├── app/                    ← Core application (Python code)
│   ├── src/               ← Source code (app.py, models.py, etc.)
│   ├── templates/         ← Flask templates
│   ├── static/            ← CSS, JS, images
│   ├── tests/             ← Test suite
│   ├── docs/              ← Documentation
│   │   ├── architecture/  ← Design docs
│   │   ├── phase-reports/ ← Historical project phases
│   │   ├── deployment/    ← Deployment guides
│   │   └── operations/    ← Operational procedures
│   ├── logs/              ← Runtime logs
│   ├── courses → ../courses (symlink)
│   ├── epub → ../epub (symlink)
│   ├── pytest.ini
│   └── requirements.txt
├── courses/               ← Course media (local for now, cloud later)
├── epub/                  ← Ebook files (local for now, cloud later)
├── .gitignore
├── LICENSE.txt
└── POST-REFACTOR_GUIDE.md (this file)
```

## Running the Application

### Start Flask Server
```bash
# From project root
cd "C:\Users\nissa\Desktop\HTML5 Project for courses"
python -m app.src.app
```

The application will be accessible at: http://localhost:5000

### Run Tests
```bash
# From project root
cd "C:\Users\nissa\Desktop\HTML5 Project for courses\app"
pytest tests/ -v
```

### Run Build Script (Populate Database)
```bash
# From project root
cd "C:\Users\nissa\Desktop\HTML5 Project for courses"
python -m app.src.build
```

### Install Dependencies
```bash
cd "C:\Users\nissa\Desktop\HTML5 Project for courses\app"
pip install -r requirements.txt
```

## Key Changes

### 1. Import Structure
All Python imports now use the `app.src.*` package structure:

```python
# Correct imports (from project root)
from app.src.app import app
from app.src.models import User, Course
from app.src.config import config
from app.src.database import db
```

Within the `app.src` package itself, modules use relative imports:
```python
# Within app/src/*.py files
from .app import app
from .models import User
from .config import config
```

### 2. File Structure
- **Python source code:** `app/src/`
- **Templates:** `app/templates/`
- **Static files:** `app/static/`
- **Tests:** `app/tests/`
- **Configuration:** `app/src/config.py`
- **Logging:** `app/src/logging_config.py`
- **Database:** `app/src/database.db` (created at runtime)

### 3. Data Access via Symlinks
Media files (courses/, epub/) are accessible via symlinks in the app directory:
- `app/courses/` → `../courses` (28 courses)
- `app/epub/` → `../epub` (54 ebooks)

This structure allows easy migration to cloud storage in future phases without changing application code.

### 4. Flask Configuration
The Flask app is now configured with explicit paths to templates and static directories:

```python
app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')
```

### 5. Documentation Organization
Documentation is now organized into logical categories:
- `app/docs/architecture/` - System design and architecture
- `app/docs/phase-reports/` - Historical project phase documentation
- `app/docs/deployment/` - Deployment checklists and guides
- `app/docs/operations/` - Operational procedures and security

## Future Cloud Migration

When moving to cloud storage (AWS S3, Azure Blob, etc.):

### Option 1: Update Symlinks
Update symlinks to point to mounted cloud storage:
```bash
# Remove local symlinks
rm app/courses app/epub

# Create new symlinks to cloud-mounted directories
ln -s /mnt/cloud-storage/courses app/courses
ln -s /mnt/cloud-storage/epub app/epub
```

### Option 2: Update Configuration
Add cloud storage paths to `app/src/config.py`:
```python
import os

class Config:
    # Cloud storage paths
    COURSES_BASE_PATH = os.getenv('COURSES_PATH', '../courses')
    EPUB_BASE_PATH = os.getenv('EPUB_PATH', '../epub')

class ProductionConfig(Config):
    COURSES_BASE_PATH = 's3://your-bucket/courses'
    EPUB_BASE_PATH = 's3://your-bucket/epub'
```

Update application code to use these paths instead of hardcoded relative paths.

## Verification Checklist

After refactoring, verify:
- [ ] Flask app starts without errors: `python -m app.src.app`
- [ ] All tests pass: `cd app && pytest tests/ -v`
- [ ] Courses accessible: Navigate to courses page in browser
- [ ] Ebooks accessible: Navigate to ebook library in browser
- [ ] Static files load: CSS, JS, images display correctly
- [ ] Symlinks working: `ls app/courses` shows course directories
- [ ] Database accessible: Can login, register, view content

## Common Commands

### Development Workflow
```bash
# Start development server
python -m app.src.app

# Run specific test
cd app && pytest tests/test_app.py -v

# Run tests with coverage
cd app && pytest tests/ --cov=src --cov-report=html

# Populate database from course/ebook files
python -m app.src.build
```

### Database Management
```bash
# Initialize database migrations (if not already done)
cd "C:\Users\nissa\Desktop\HTML5 Project for courses"
python -m flask --app app.src.app db init

# Create migration
python -m flask --app app.src.app db migrate -m "Description"

# Apply migrations
python -m flask --app app.src.app db upgrade
```

### Logging
```bash
# View recent logs
cat app/logs/app.log

# Analyze logs (if log_analyzer.py is available)
python log_analyzer.py --since 1h
```

## Troubleshooting

### Import Errors
**Error:** `ModuleNotFoundError: No module named 'app'`

**Solution:** Always run Python commands from the project root:
```bash
cd "C:\Users\nissa\Desktop\HTML5 Project for courses"
python -m app.src.app
```

### Symlink Issues
**Error:** Courses or ebooks not loading

**Solution:** Verify symlinks exist:
```bash
ls -la app/ | grep -E "courses|epub"
```

Should show:
```
drwxr-xr-x ... courses -> ../courses
drwxr-xr-x ... epub -> ../epub
```

If missing, recreate:
```bash
cd app
ln -s ../courses courses
ln -s ../epub epub
```

### Template Not Found
**Error:** `jinja2.exceptions.TemplateNotFound`

**Solution:** Ensure Flask app is configured with correct template path. The Flask app initialization includes:
```python
app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')
```

### Static Files Not Loading
**Error:** 404 on CSS/JS files

**Solution:** Verify static folder path in Flask app configuration (see above).

## Migration Notes

### From Old Structure
If you have any old imports or references, update them:

**Old:**
```python
from app import app
from models import User
```

**New:**
```python
from app.src.app import app
from app.src.models import User
```

### Running Tests
Tests now expect the new structure. Update test runner commands:

**Old:**
```bash
pytest tests/
```

**New:**
```bash
cd app
pytest tests/
```

Or from project root:
```bash
pytest app/tests/
```

## Next Steps

1. **Verify functionality:** Run the application and test all features
2. **Run test suite:** Ensure all tests pass with new structure
3. **Update documentation:** Add any project-specific notes to this guide
4. **Begin Phase 2:** Email verification, password reset, HTTPS implementation

## Support

For questions or issues with the refactored structure:
1. Check `app/docs/REFACTORING_CHECKLIST.md` for detailed changes
2. Review `app/docs/NAVIGATION.md` for documentation index
3. Refer to `app/docs/architecture/` for system design
4. Check phase reports in `app/docs/phase-reports/` for historical context
