// Admin Panel JavaScript

// CSRF token management
let csrfToken = null;

// Fetch CSRF token on page load
async function initCSRFToken() {
    try {
        const response = await fetch('/csrf-token');
        const data = await response.json();
        csrfToken = data.csrf_token;
    } catch (error) {
        console.error('Failed to fetch CSRF token:', error);
    }
}

// Helper function to add log line
function addLog(elementId, message, type = 'info') {
    const logContainer = document.getElementById(elementId);
    if (!logContainer) return;

    const logLine = document.createElement('div');
    logLine.className = `log-line log-${type}`;
    logLine.textContent = message;
    logContainer.appendChild(logLine);

    // Auto-scroll to bottom
    logContainer.parentElement.scrollTop = logContainer.parentElement.scrollHeight;
}

// Clear log
function clearLog(elementId) {
    const logContainer = document.getElementById(elementId);
    if (logContainer) logContainer.innerHTML = '';
}

// Switch to specific tab
function switchToTab(tabName) {
    const tab = document.getElementById(`${tabName}-tab`);
    if (tab) tab.click();
}

// ===========================
// TEXTBOOK FUNCTIONS
// ===========================

async function scanTextbooks() {
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Scanning...';

    const progressDiv = document.getElementById('textbook-progress');
    const logDiv = document.getElementById('textbook-log');
    progressDiv.style.display = 'block';
    logDiv.innerHTML = '';

    try {
        addLog('textbook-log', 'Scanning /epub directory for EPUB files...', 'info');

        const response = await fetch('/api/admin/scan-ebooks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        const data = await response.json();

        if (response.ok) {
            addLog('textbook-log', `Found ${data.total} textbooks`, 'success');
            addLog('textbook-log', `New: ${data.new}, Already imported: ${data.existing}`, 'info');

            // Load textbooks table
            await loadTextbooksTable();
        } else {
            addLog('textbook-log', `Error: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog('textbook-log', `Error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Scan Textbook Library';
    }
}

async function loadTextbooksTable() {
    try {
        const response = await fetch('/api/admin/get-ebooks');
        const data = await response.json();

        const tbody = document.getElementById('textbooks-tbody');
        tbody.innerHTML = '';

        if (data.ebooks && data.ebooks.length > 0) {
            data.ebooks.forEach(ebook => {
                const row = document.createElement('tr');
                const hasCover = ebook.cover_status === 'found';
                const statusBadge = hasCover ?
                    '<span class="badge bg-success">Real</span>' :
                    '<span class="badge bg-warning text-dark">Generated</span>';

                row.innerHTML = `
                    <td>${ebook.title}</td>
                    <td>${ebook.author || 'Unknown'}</td>
                    <td>${statusBadge}</td>
                    <td>${ebook.created_at}</td>
                    <td>
                        <button class="btn btn-sm btn-info" onclick="searchBookCover(${ebook.id})">Search Cover</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteBook(${ebook.id})">Delete</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading textbooks:', error);
    }
}

function showCoverSearch() {
    document.getElementById('cover-search-div').style.display = 'block';
}

function cancelSearchCovers() {
    document.getElementById('cover-search-div').style.display = 'none';
}

async function executeSearchCovers() {
    const source = document.getElementById('cover-source').value;
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Searching...';

    const logDiv = document.getElementById('textbook-log');
    const progressDiv = document.getElementById('textbook-progress');
    progressDiv.style.display = 'block';
    logDiv.innerHTML = '';

    addLog('textbook-log', `Searching for covers using ${source}...`, 'info');

    try {
        const response = await fetch('/api/admin/search-covers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ source })
        });

        const data = await response.json();

        if (response.ok) {
            addLog('textbook-log', `Found ${data.found} covers`, 'success');
            addLog('textbook-log', `Failed: ${data.failed}, Skipped: ${data.skipped}`, 'info');
            await loadTextbooksTable();
        } else {
            addLog('textbook-log', `Error: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog('textbook-log', `Error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Search All Missing Covers';
    }
}

async function generatePlaceholders() {
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Generating...';

    const logDiv = document.getElementById('textbook-log');
    const progressDiv = document.getElementById('textbook-progress');
    progressDiv.style.display = 'block';
    logDiv.innerHTML = '';

    addLog('textbook-log', 'Generating placeholder covers...', 'info');

    try {
        const response = await fetch('/api/admin/generate-covers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        const data = await response.json();

        if (response.ok) {
            addLog('textbook-log', `Generated ${data.generated} placeholder covers`, 'success');
            await loadTextbooksTable();
        } else {
            addLog('textbook-log', `Error: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog('textbook-log', `Error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Generate Placeholders';
    }
}

function searchBookCover(bookId) {
    alert('Individual book cover search coming soon');
}

function deleteBook(bookId) {
    if (confirm('Delete this textbook?')) {
        alert('Delete coming soon');
    }
}

// ===========================
// COURSE FUNCTIONS
// ===========================

async function scanCourses() {
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Scanning...';

    const progressDiv = document.getElementById('course-progress');
    const logDiv = document.getElementById('course-log');
    progressDiv.style.display = 'block';
    logDiv.innerHTML = '';

    addLog('course-log', 'Scanning /courses directory...', 'info');

    try {
        const response = await fetch('/api/admin/scan-courses', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        const data = await response.json();

        if (response.ok) {
            addLog('course-log', `Found ${data.total} courses`, 'success');
            addLog('course-log', `New: ${data.new}, Already imported: ${data.existing}`, 'info');
            await loadCoursesTable();
        } else {
            addLog('course-log', `Error: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog('course-log', `Error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Scan Courses Directory';
    }
}

async function loadCoursesTable() {
    try {
        const response = await fetch('/api/admin/get-courses');
        const data = await response.json();

        const tbody = document.getElementById('courses-tbody');
        tbody.innerHTML = '';

        if (data.courses && data.courses.length > 0) {
            data.courses.forEach(course => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${course.title}</td>
                    <td>${course.has_thumbnail ? '<span class="badge bg-success">Yes</span>' : '<span class="badge bg-warning text-dark">No</span>'}</td>
                    <td>${course.categories || 'Uncategorized'}</td>
                    <td>${course.created_at}</td>
                    <td>
                        <button class="btn btn-sm btn-warning" onclick="regenerateThumb(${course.id})">Regen Thumb</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteCourse(${course.id})">Delete</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading courses:', error);
    }
}

async function generateThumbnails() {
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Generating...';

    const logDiv = document.getElementById('course-log');
    const progressDiv = document.getElementById('course-progress');
    progressDiv.style.display = 'block';
    logDiv.innerHTML = '';

    addLog('course-log', 'Generating course thumbnails...', 'info');

    try {
        const response = await fetch('/api/admin/generate-thumbnails', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        const data = await response.json();

        if (response.ok) {
            addLog('course-log', `Generated ${data.generated} thumbnails`, 'success');
            addLog('course-log', `Failed: ${data.failed}`, 'info');
            await loadCoursesTable();
        } else {
            addLog('course-log', `Error: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog('course-log', `Error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Generate Thumbnails';
    }
}

async function autoCategorize() {
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Categorizing...';

    const logDiv = document.getElementById('course-log');
    const progressDiv = document.getElementById('course-progress');
    progressDiv.style.display = 'block';
    logDiv.innerHTML = '';

    addLog('course-log', 'Auto-categorizing courses...', 'info');

    try {
        const response = await fetch('/api/admin/autocategorize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        const data = await response.json();

        if (response.ok) {
            addLog('course-log', `Categorized ${data.updated} courses`, 'success');
            await loadCoursesTable();
        } else {
            addLog('course-log', `Error: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog('course-log', `Error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Auto-Categorize Courses';
    }
}

function regenerateThumb(courseId) {
    alert('Individual thumbnail regeneration coming soon');
}

function deleteCourse(courseId) {
    if (confirm('Delete this course?')) {
        alert('Delete coming soon');
    }
}

// ===========================
// SERVER FUNCTIONS
// ===========================

async function restartServer() {
    if (!confirm('Restart server? This will briefly disconnect users.')) return;

    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Restarting...';

    try {
        const response = await fetch('/api/admin/server/restart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        const data = await response.json();

        if (response.ok) {
            alert('Server restarting...');
            setTimeout(() => location.reload(), 2000);
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Restart Server';
    }
}

async function startDevMode() {
    if (!confirm('Start development mode? Debug features will be enabled.')) return;
    alert('Coming soon');
}

async function startProdMode() {
    if (!confirm('Start production mode? Debug features will be disabled.')) return;
    alert('Coming soon');
}

async function stopServer() {
    if (!confirm('Stop server? Application will go offline.')) return;
    alert('Coming soon');
}

async function runDiagnostics() {
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Running...';

    const outputDiv = document.getElementById('diagnostics-output');
    const logDiv = document.getElementById('diagnostics-log');
    outputDiv.style.display = 'block';
    logDiv.innerHTML = '';

    addLog('diagnostics-log', 'Running system diagnostics...', 'info');

    try {
        const response = await fetch('/api/admin/diagnostics');
        const data = await response.json();

        if (response.ok) {
            addLog('diagnostics-log', `Database: ${data.database_status}`, 'success');
            addLog('diagnostics-log', `Courses: ${data.courses_count}`, 'info');
            addLog('diagnostics-log', `Ebooks: ${data.ebooks_count}`, 'info');
            addLog('diagnostics-log', `Covers: ${data.covers_count}`, 'info');
            addLog('diagnostics-log', `Thumbnails: ${data.thumbnails_count}`, 'info');

            if (data.missing_covers > 0) {
                addLog('diagnostics-log', `Warning: ${data.missing_covers} missing covers`, 'error');
            }
        } else {
            addLog('diagnostics-log', `Error: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog('diagnostics-log', `Error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Run Diagnostics';
    }
}

async function fetchLogs() {
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Fetching...';

    const outputDiv = document.getElementById('logs-output');
    const contentDiv = document.getElementById('logs-content');
    outputDiv.style.display = 'block';
    contentDiv.innerHTML = '';

    try {
        const response = await fetch('/api/admin/logs');
        const data = await response.json();

        if (response.ok && data.logs) {
            data.logs.forEach(line => {
                const logLine = document.createElement('div');
                logLine.className = 'log-line';
                logLine.textContent = line;
                contentDiv.appendChild(logLine);
            });
        } else {
            contentDiv.textContent = 'No logs available';
        }
    } catch (error) {
        contentDiv.textContent = `Error: ${error.message}`;
    } finally {
        btn.disabled = false;
        btn.textContent = 'Fetch Latest Logs';
    }
}

// ===========================
// DASHBOARD FUNCTIONS
// ===========================

async function loadDashboard() {
    try {
        const response = await fetch('/api/admin/status');
        const data = await response.json();

        document.getElementById('stat-courses').textContent = data.courses_count || '0';
        document.getElementById('stat-textbooks').textContent = data.ebooks_count || '0';
        document.getElementById('stat-covers').textContent = data.covers_with_real_images || '0';
        document.getElementById('stat-server').textContent = data.server_status === 'running' ? 'Running' : 'Stopped';
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// ===========================
// USER MANAGEMENT
// ===========================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize CSRF token
    initCSRFToken();

    // Load initial dashboard
    loadDashboard();

    // Delete user buttons
    document.querySelectorAll('.delete-user-btn').forEach(button => {
        button.addEventListener('click', async (event) => {
            const userId = event.target.dataset.userId;
            const username = event.target.dataset.username;

            if (confirm(`Delete user '${username}'?`)) {
                try {
                    const response = await fetch('/api/admin/delete_user', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({ user_id: userId }),
                    });

                    const result = await response.json();

                    if (response.ok) {
                        alert(result.message);
                        location.reload();
                    } else {
                        alert(`Error: ${result.error}`);
                    }
                } catch (error) {
                    alert(`Error: ${error.message}`);
                }
            }
        });
    });

    // Load layout settings when tab is opened
    const layoutTab = document.getElementById('layout-tab');
    if (layoutTab) {
        layoutTab.addEventListener('click', loadLayoutSettings);
    }
});

// ===========================
// LAYOUT CONFIGURATION FUNCTIONS
// ===========================

async function loadLayoutSettings() {
    try {
        const response = await fetch('/api/admin/layout/get');
        const data = await response.json();

        if (data.success && data.settings) {
            const settings = data.settings;
            document.getElementById('courses-width').value = settings.featured_courses_width || '100%';
            document.getElementById('courses-max-width').value = settings.featured_courses_max_width || '600px';
            document.getElementById('course-img-width').value = settings.course_image_width || '150px';
            document.getElementById('course-font').value = settings.course_title_font_size || '1rem';

            document.getElementById('ebooks-width').value = settings.featured_ebooks_width || '100%';
            document.getElementById('ebooks-max-width').value = settings.featured_ebooks_max_width || '600px';
            document.getElementById('ebook-img-width').value = settings.ebook_image_width || '120px';
            document.getElementById('ebook-img-height').value = settings.ebook_image_height || '150px';

            document.getElementById('table-padding').value = settings.table_padding || '12px';
            document.getElementById('table-gap').value = settings.table_gap || '0.75rem';
            document.getElementById('card-background').value = settings.card_background || 'transparent';
        }
    } catch (error) {
        console.error('Error loading layout settings:', error);
    }
}

async function saveLayoutSettings() {
    try {
        const settings = {
            featured_courses_width: document.getElementById('courses-width').value,
            featured_courses_max_width: document.getElementById('courses-max-width').value,
            course_image_width: document.getElementById('course-img-width').value,
            course_title_font_size: document.getElementById('course-font').value,

            featured_ebooks_width: document.getElementById('ebooks-width').value,
            featured_ebooks_max_width: document.getElementById('ebooks-max-width').value,
            ebook_image_width: document.getElementById('ebook-img-width').value,
            ebook_image_height: document.getElementById('ebook-img-height').value,

            table_padding: document.getElementById('table-padding').value,
            table_gap: document.getElementById('table-gap').value,
            card_background: document.getElementById('card-background').value,
        };

        const response = await fetch('/api/admin/layout/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ settings })
        });

        const data = await response.json();

        if (data.success) {
            const msgDiv = document.getElementById('layout-message');
            msgDiv.innerHTML = '<div class="alert alert-success">Settings saved successfully! Refresh the page to see changes.</div>';
            msgDiv.scrollIntoView({ behavior: 'smooth' });
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function resetLayoutSettings() {
    if (!confirm('Reset all layout settings to defaults? This cannot be undone.')) return;

    try {
        const response = await fetch('/api/admin/layout/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        const data = await response.json();

        if (data.success && data.settings) {
            const settings = data.settings;
            document.getElementById('courses-width').value = settings.featured_courses_width;
            document.getElementById('courses-max-width').value = settings.featured_courses_max_width;
            document.getElementById('course-img-width').value = settings.course_image_width;
            document.getElementById('course-font').value = settings.course_title_font_size;

            document.getElementById('ebooks-width').value = settings.featured_ebooks_width;
            document.getElementById('ebooks-max-width').value = settings.featured_ebooks_max_width;
            document.getElementById('ebook-img-width').value = settings.ebook_image_width;
            document.getElementById('ebook-img-height').value = settings.ebook_image_height;

            document.getElementById('table-padding').value = settings.table_padding;
            document.getElementById('table-gap').value = settings.table_gap;
            document.getElementById('card-background').value = settings.card_background;

            const msgDiv = document.getElementById('layout-message');
            msgDiv.innerHTML = '<div class="alert alert-info">Settings reset to defaults. Refresh the page to see changes.</div>';
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

function previewLayoutSettings() {
    const msgDiv = document.getElementById('layout-message');
    msgDiv.innerHTML = '<div class="alert alert-info">Preview feature coming soon! Save settings and refresh to see changes on the homepage.</div>';
}
