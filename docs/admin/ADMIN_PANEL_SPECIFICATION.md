# Admin Panel Specification & Function Catalog

## PROJECT FUNCTIONS & SCRIPTS INVENTORY

### CATEGORY 1: E-BOOK/TEXTBOOK MANAGEMENT

#### Scanning & Import Functions
- **Script:** `app/src/extract_metadata.py::process_all_ebooks()`
  - **Purpose:** Scans `/epub` directory for new .epub files
  - **What it does:** Lists all EPUB files, extracts metadata
  - **Admin Control:** "Scan Textbook Library" button
  - **Output:** JSON report of found books

- **Function:** `app/src/build.py::process_ebooks()`
  - **Purpose:** Core EPUB processing pipeline
  - **What it does:**
    - Scans EPUB directory
    - Extracts embedded covers
    - Searches for covers via APIs
    - Generates placeholder covers
    - Saves to database
  - **Admin Control:** "Import & Process All Textbooks" button

#### Metadata Extraction Functions
- **Function:** `app/src/build.py::extract_epub_metadata()`
  - **Purpose:** Extract title, author, ISBN from EPUB file
  - **Admin Control:** Displayed in admin details/preview

- **Function:** `app/src/extract_metadata.py::extract_epub_metadata()`
  - **Purpose:** Enhanced metadata extraction (same as above, refactored)

#### Cover Fetching Functions
- **Function:** `app/src/build.py::fetch_cover_from_google_books()`
  - **Purpose:** Search Google Books API by ISBN or title+author
  - **Admin Control:** "Search Covers - Google Books" button
  - **Success Rate:** ~98% with ISBN, ~85% without

- **Function:** `app/src/build.py::fetch_cover_from_openlibrary()`
  - **Purpose:** Fallback - Search Open Library API
  - **Admin Control:** "Search Covers - Open Library" button
  - **Success Rate:** ~48% overall

- **Function:** `app/src/build.py::download_cover_image()`
  - **Purpose:** Download cover image from URL, validate size (≥5KB)
  - **Admin Control:** Automatic/called by search functions

- **Function:** `app/src/extract_metadata.py::fetch_cover_from_archive_org()`
  - **Purpose:** Alternative source - archive.org (internet archive)
  - **Admin Control:** "Search Covers - Archive.org" button (fallback)

- **Function:** `app/src/extract_metadata.py::fetch_cover_from_bookcovers_io()`
  - **Purpose:** Alternative source - bookcovers.io
  - **Admin Control:** "Search Covers - BookCovers.io" button (fallback)

#### Cover Generation Functions
- **Function:** `app/src/build.py::generate_cover_image()`
  - **Purpose:** Create PIL placeholder cover with book title
  - **Admin Control:** "Generate Placeholder Cover" button (for each book)

### CATEGORY 2: COURSE MANAGEMENT

#### Course Scanning & Import
- **Function:** `app/src/build.py::parse_course_metadata()`
  - **Purpose:** Extract course title, description, intro video from HTML
  - **What it does:** Reads course package index.html, parses BeautifulSoup
  - **Admin Control:** "Scan Courses Directory" button

- **Function:** `app/src/build.py::main()` (courses section)
  - **Purpose:** Complete course import pipeline
  - **What it does:**
    - Scans `/courses` directory
    - Extracts metadata from each course
    - Generates thumbnails from intro videos
    - Adds to database

#### Thumbnail Generation
- **Function:** `app/src/build.py::generate_thumbnail()`
  - **Purpose:** Generate video thumbnail from course intro video using ffmpeg
  - **What it does:**
    - Probes video duration
    - Captures frame at 10% mark
    - Saves as JPG in `/static/thumbnails`
  - **Admin Control:** "Generate Course Thumbnails" button

#### Category Assignment
- **Function:** `app/src/build.py::categories_from_name()`
  - **Purpose:** Auto-assign categories based on regex keyword matching
  - **Patterns:** Python, Java, C++, JavaScript, DevOps, Data Structures, Rust, Linux, AI
  - **Admin Control:** "Auto-Categorize Courses" button (can be overridden)

### CATEGORY 3: DATABASE OPERATIONS

#### Database Population
- **Script:** `populate_db.py`
  - **Purpose:** Main entry point for entire data import workflow
  - **What it does:** Calls `app/src/build.py::main()` with app context
  - **Admin Control:** "Full Import (Courses + Textbooks)" button

#### Database Management
- **Function:** `app/src/database.py::init_db()`
  - **Purpose:** Initialize database if not exists
  - **Admin Control:** "Initialize Database" button (on first setup)

- **Function:** `app/src/database.py::db.create_all()`
  - **Purpose:** Create all tables (if missing)
  - **Admin Control:** "Create Database Tables" button

### CATEGORY 4: SERVER & DIAGNOSTICS

#### Server Control (TO BE CREATED)
- **Script:** `app/src/server_control.py` (NEEDED)
  - **Functions needed:**
    - `start_development_server()` - Start Flask with debug=True
    - `start_production_server()` - Start Flask with debug=False
    - `restart_server()` - Kill and restart server
    - `get_server_status()` - Check if running, get PID
    - `kill_server()` - Force stop

#### Diagnostics & Logging (TO BE CREATED)
- **Script:** `app/src/diagnostics.py` (NEEDED)
  - **Functions needed:**
    - `get_application_logs()` - Read recent error/info logs
    - `get_system_status()` - CPU, memory, disk usage
    - `get_file_counts()` - Count covers, courses, ebooks files
    - `validate_data_integrity()` - Check DB vs filesystem
    - `get_last_import_status()` - Success/failure counts

#### Error Recovery (TO BE CREATED)
- **Script:** `app/src/error_recovery.py` (NEEDED)
  - **Functions needed:**
    - `rollback_last_import()` - Undo database changes
    - `reprocess_failed_books()` - Retry cover search for books that failed
    - `reprocess_failed_courses()` - Retry thumbnail generation
    - `orphan_file_cleanup()` - Remove covers/thumbnails with no DB entry

### CATEGORY 5: UTILITY & ANALYSIS

#### Analytics & Reporting (TO BE CREATED)
- **Script:** `app/src/analytics.py` (NEEDED)
  - **Functions needed:**
    - `get_library_statistics()` - Total courses, books, categories breakdown
    - `get_cover_statistics()` - # with real covers, # with generated, # missing
    - `get_category_distribution()` - How many per category
    - `export_library_manifest()` - CSV/JSON export of all content

#### Content Validation (EXISTING)
- **Script:** `app/src/extract_metadata.py::process_all_ebooks()`
  - Can output JSON with success/failure info

---

## PROPOSED ADMIN PANEL STRUCTURE

### Dashboard/Home Section
- **Widget:** Library Overview Card
  - Total courses, total books, total categories
  - Last import timestamp
  - % with covers, % with generated covers

- **Widget:** Quick Stats
  - Storage usage (covers directory size)
  - Server status (running/stopped, uptime)
  - Database size

### 1. TEXTBOOK MANAGEMENT TAB

#### Sub-section: Library Overview
- **Table:** All textbooks with:
  - Title, Author, ISBN
  - Cover status (real/generated/missing)
  - Date added
  - Categories
  - Actions: View, Edit, Delete, Re-process

#### Sub-section: Bulk Operations
- **Button:** "Scan Textbook Library"
  - Shows: New books found, books already in library
  - Option to "Import All"

- **Button:** "Search for Covers"
  - Dropdown to select source:
    - Google Books (default)
    - Open Library
    - Archive.org
    - BookCovers.io
  - Shows progress: "Searching [1-9 of 54]..."
  - Results: Successful, Failed, Skipped counts
  - Ability to "Retry Failed" subset

- **Button:** "Generate Placeholder Covers"
  - For books that have no cover found
  - Shows: [Book Title] generating...
  - Results count

#### Sub-section: Single Book Operations
- Search bar to find specific book
- For each book:
  - Preview cover image
  - View metadata (title, author, ISBN)
  - "Search Cover for This Book" dropdown
  - "Generate Placeholder" button
  - "Refresh Metadata" button
  - "Delete from Library" button

### 2. COURSE MANAGEMENT TAB

#### Sub-section: Courses Library
- **Table:** All courses with:
  - Title, Description (truncated)
  - Thumbnail status (generated/missing)
  - Categories
  - Video path
  - Date added
  - Actions: View, Edit, Delete, Re-process

#### Sub-section: Bulk Operations
- **Button:** "Scan Courses Directory"
  - Shows: New courses found, courses already in system
  - List of courses to import with preview metadata
  - Option to "Import Selected" or "Import All"

- **Button:** "Generate Course Thumbnails"
  - For all courses missing thumbnails
  - Shows progress: "[Course Name] generating thumbnail..."
  - Results: Successful, Failed, Skipped

- **Button:** "Auto-Categorize All Courses"
  - Applies keyword matching to all courses
  - Shows changes: [Course] → [New Categories]

#### Sub-section: Single Course Operations
- Search bar to find specific course
- For each course:
  - Preview thumbnail image
  - View metadata
  - "Generate Thumbnail" button
  - "Edit Categories" button
  - "Refresh Metadata" button
  - "Delete from Library" button

### 3. SERVER & DIAGNOSTICS TAB

#### Sub-section: Server Control
- **Status Card:**
  - Server Status: Running/Stopped
  - Mode: Development/Production
  - Uptime: HH:MM:SS
  - Memory Usage: XXX MB
  - CPU Usage: XX%

- **Control Buttons:**
  - "Restart Server"
  - "Start Development Mode" (debug=True)
  - "Start Production Mode" (debug=False)
  - "Stop Server"

- **Confirmation Dialogs:** "This will briefly disconnect all users. Continue?"

#### Sub-section: System Diagnostics
- **Logs Section:**
  - Dropdown: Filter by level (All, Errors, Warnings, Info)
  - Last 50 log lines displayed
  - Refresh button
  - Export logs button

- **File System Check:**
  - Total courses found: X
  - Total ebooks found: X
  - Total covers on disk: X
  - Total thumbnails on disk: X
  - Missing covers (in DB but no file): X
  - Orphan covers (on disk but not in DB): X

  - Button: "Clean Up Orphan Files"
    - Deletes covers/thumbnails with no DB entry

#### Sub-section: Data Integrity
- **Validation Report:**
  - Database tables exist: ✓/✗
  - Courses table count: X
  - Ebooks table count: X
  - Verify all DB references exist on disk: ✓/✗

  - Button: "Run Full Validation"
    - Shows detailed report

### 4. SETTINGS & CONFIGURATION TAB (Optional but useful)

#### Sub-section: Import Settings
- Checkbox: "Auto-generate covers if not found"
- Dropdown: "Default cover source" (Google Books, Open Library, etc.)
- Number input: "Timeout for API requests (seconds)"
- Checkbox: "Enable detailed logging"

#### Sub-section: Database Settings
- Current database location: /path/to/database.db
- Backup database button
- Button: "Reset Database" (with warning)

#### Sub-section: Content Settings
- Auto-categorize new courses: On/Off
- Default category for uncategorized items: [Dropdown]

### 5. REPORTS & ANALYTICS TAB (Optional but valuable)

#### Sub-section: Library Statistics
- **Chart:** Books by category (pie chart)
- **Chart:** Courses by category (pie chart)
- **Stat:** Total content size
- **Stat:** % of books with real covers vs generated
- **Table:** Category breakdown with counts

#### Sub-section: Import History
- **Timeline:**
  - Last import: [Date/Time]
  - Status: Success/Failed
  - Books imported: X, Covers found: Y, Generated: Z
  - Courses imported: X, Thumbnails: Y

- Full history table with sortable columns

#### Sub-section: Export/Backup
- Button: "Export Library Manifest (CSV)"
  - Downloads list of all courses & books
- Button: "Export Statistics Report (PDF)"
- Button: "Backup Database"
  - Creates timestamped backup in `/backups`

---

## REQUIRED NEW SCRIPTS TO CREATE

### 1. `app/src/server_control.py`
```
start_dev_server()
start_prod_server()
restart_server()
kill_server()
get_server_status()
get_server_logs()
```

### 2. `app/src/admin_api.py`
```
API endpoints for all admin panel operations:
- POST /api/admin/scan-ebooks
- POST /api/admin/search-covers
- POST /api/admin/generate-covers
- POST /api/admin/scan-courses
- POST /api/admin/generate-thumbnails
- POST /api/admin/autocategorize-courses
- GET /api/admin/status
- POST /api/admin/server/restart
- GET /api/admin/diagnostics
- POST /api/admin/validate-data
- POST /api/admin/cleanup-orphans
- GET /api/admin/statistics
- POST /api/admin/export-manifest
```

### 3. `app/src/diagnostics.py`
```
get_application_logs()
get_system_status()
get_file_counts()
validate_data_integrity()
get_last_import_status()
check_api_connectivity()
get_database_stats()
```

### 4. `app/src/error_recovery.py`
```
rollback_last_import()
reprocess_failed_books()
reprocess_failed_courses()
cleanup_orphan_files()
repair_database()
```

### 5. `app/src/analytics.py`
```
get_library_statistics()
get_cover_statistics()
get_category_distribution()
export_library_manifest()
get_import_history()
```

### 6. `app/templates/admin.html` (NEW)
- Admin dashboard HTML with all tabs and controls
- Responsive design
- Real-time progress indicators

### 7. `app/static/js/admin.js` (NEW)
- JavaScript for admin panel interactions
- API calls to backend
- Progress bars for long operations
- Real-time log streaming

---

## ADMIN PANEL WORKFLOW EXAMPLES

### Scenario 1: Adding a New Textbook
```
1. User drops .epub file into /epub directory
2. User goes to Admin Panel → Textbooks → "Scan Textbook Library"
3. System shows: "1 new book found: 'My New Book'"
4. User clicks "Import"
5. System displays metadata and cover preview (or "No cover found")
6. If no cover:
   - User clicks "Search for Covers"
   - System tries Google Books → finds cover
   - Cover displayed in preview
7. User clicks "Import & Save"
8. Book appears in textbooks library with cover
```

### Scenario 2: Adding a New Course
```
1. User adds new course folder to /courses
2. User goes to Admin Panel → Courses → "Scan Courses Directory"
3. System shows: "1 new course found: 'Advanced Python'"
4. User sees preview: title, description, video path
5. User clicks "Import"
6. System:
   - Extracts metadata from course index.html
   - Generates thumbnail from intro video
   - Auto-assigns categories
7. Course appears in courses library with thumbnail
```

### Scenario 3: Troubleshooting Missing Covers
```
1. Admin notices 9 books have generated covers
2. Goes to Admin Panel → Textbooks → "Search for Covers"
3. Selects source: "Google Books"
4. Clicks "Retry Failed Books"
5. System shows progress: [1-9 of 9]
6. Results: "Found 5 more covers"
7. 4 books remain with generated covers (acceptable)
```

### Scenario 4: Server Diagnostics
```
1. Application acting slow
2. Admin goes to Admin Panel → Server & Diagnostics
3. Sees: Memory 85%, CPU 60%, Uptime 72h
4. Clicks "View Recent Logs"
5. Sees error: "API timeout from Google Books"
6. Goes to Settings, increases "API timeout" from 5s to 10s
7. Clicks "Restart Server" → Mode: Production
8. Server restarts in production mode
```

---

## BENEFITS OF THIS ADMIN PANEL

1. **No Code Knowledge Required** - Admin can manage library with UI, not CLI
2. **Reduced Token Usage** - You can walk away, admin can maintain content
3. **Batch Operations** - Process all 54 books at once, not one by one
4. **Error Recovery** - Can retry failed imports, cleanup orphans
5. **Visibility** - See what's failing, what's succeeding in real-time
6. **Self-Service** - Admin doesn't need to call you for routine tasks
7. **Scalability** - As library grows to 200+ books, admin tools become essential
8. **Diagnostics** - Quick troubleshooting without needing Claude context

---

## IMPLEMENTATION PRIORITY

**Phase 1 (Essential):**
- Server Control tab (restart, dev/prod modes)
- Scan & Import buttons (ebooks, courses)
- Cover search dropdown
- Basic statistics dashboard

**Phase 2 (Important):**
- Diagnostics tab (logs, file validation)
- Error recovery functions
- Single item management (edit, delete)
- Analytics & reports

**Phase 3 (Nice to have):**
- Settings & configuration
- Advanced export/backup
- Import history timeline
- API connectivity testing
