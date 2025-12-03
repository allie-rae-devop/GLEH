// Admin Panel JavaScript - Refactored for new admin panel

// CSRF token management
let csrfToken = null;
let envConfig = {};

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
// DASHBOARD FUNCTIONS
// ===========================

async function loadDashboard() {
    try {
        const response = await fetch('/api/admin/status');
        const data = await response.json();

        document.getElementById('stat-courses').textContent = data.courses_count || '0';
        document.getElementById('stat-textbooks').textContent = data.ebooks_count || '0';
        document.getElementById('stat-users').textContent = data.users_count || '0';
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Environment Configuration Functions
async function loadEnvConfig() {
    try {
        const response = await fetch('/api/admin/env-config');
        const data = await response.json();

        if (response.ok && data.config) {
            envConfig = data.config;
            renderEnvConfigTable();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

function renderEnvConfigTable() {
    const tbody = document.getElementById('env-config-tbody');
    tbody.innerHTML = '';

    for (const [key, value] of Object.entries(envConfig)) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><input type="text" class="form-control env-config-input" value="${key}" data-key="${key}" onchange="updateEnvKey(this)"></td>
            <td><input type="text" class="form-control env-config-input" value="${value}" data-key="${key}" onchange="updateEnvValue(this)"></td>
            <td><button class="btn btn-sm btn-danger" onclick="deleteEnvVariable('${key}')">Delete</button></td>
        `;
        tbody.appendChild(row);
    }
}

function updateEnvKey(input) {
    const oldKey = input.getAttribute('data-key');
    const newKey = input.value.trim();

    if (newKey && newKey !== oldKey) {
        envConfig[newKey] = envConfig[oldKey];
        delete envConfig[oldKey];
        input.setAttribute('data-key', newKey);

        // Update corresponding value input
        const row = input.closest('tr');
        const valueInput = row.querySelector('input[type="text"]:nth-child(2)');
        if (valueInput) {
            valueInput.setAttribute('data-key', newKey);
        }
    }
}

function updateEnvValue(input) {
    const key = input.getAttribute('data-key');
    envConfig[key] = input.value;
}

function deleteEnvVariable(key) {
    if (confirm(`Delete variable '${key}'?`)) {
        delete envConfig[key];
        renderEnvConfigTable();
    }
}

function addEnvVariable() {
    const key = prompt('Enter variable name:');
    if (key && key.trim()) {
        const value = prompt('Enter variable value:');
        envConfig[key.trim()] = value || '';
        renderEnvConfigTable();
    }
}

async function saveEnvConfig() {
    try {
        const response = await fetch('/api/admin/env-config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ config: envConfig })
        });

        const data = await response.json();

        if (response.ok) {
            alert('Configuration saved! Restart server for changes to take effect.');
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// ===========================
// COURSE FUNCTIONS
// ===========================

// Drag and Drop Upload
function setupCourseUpload() {
    const dropArea = document.getElementById('course-upload-area');
    const fileInput = document.getElementById('course-file-input');

    dropArea.addEventListener('click', () => fileInput.click());

    dropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropArea.classList.add('dragover');
    });

    dropArea.addEventListener('dragleave', () => {
        dropArea.classList.remove('dragover');
    });

    dropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dropArea.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            uploadCourseFile(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadCourseFile(e.target.files[0]);
        }
    });
}

async function uploadCourseFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const progressDiv = document.getElementById('upload-progress');
    const progressBar = document.getElementById('upload-progress-bar');
    progressDiv.style.display = 'block';
    progressBar.style.width = '0%';
    progressBar.textContent = '0%';

    try {
        const xhr = new XMLHttpRequest();

        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                progressBar.style.width = percent + '%';
                progressBar.textContent = percent + '%';
            }
        });

        xhr.addEventListener('load', () => {
            if (xhr.status === 200) {
                const data = JSON.parse(xhr.responseText);
                progressBar.classList.add('bg-success');
                progressBar.textContent = 'Complete!';
                alert(data.message);
                loadCoursesTable();
            } else {
                const data = JSON.parse(xhr.responseText);
                progressBar.classList.add('bg-danger');
                alert(`Error: ${data.error}`);
            }
        });

        xhr.open('POST', '/api/admin/upload-course');
        xhr.setRequestHeader('X-CSRFToken', csrfToken);
        xhr.send(formData);

    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function scanCourses() {
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Scanning...';

    const progressDiv = document.getElementById('course-progress');
    const logDiv = document.getElementById('course-log');
    progressDiv.style.display = 'block';
    clearLog('course-log');

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
        btn.textContent = 'Scan Course Directory';
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
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="deleteCourse(${course.id}, '${course.title}')">Delete</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No courses found</td></tr>';
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
    clearLog('course-log');

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
    clearLog('course-log');

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
        btn.textContent = 'Auto-Categorize';
    }
}

async function deleteCourse(courseId, title) {
    if (!confirm(`Delete course "${title}"?`)) return;

    try {
        const response = await fetch(`/api/admin/delete-course/${courseId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken
            }
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message);
            await loadCoursesTable();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// ===========================
// DIAGNOSTICS FUNCTIONS
// ===========================

async function restartServer() {
    if (!confirm('Restart server? Use docker-compose restart web from command line.')) return;

    try {
        const response = await fetch('/api/admin/server/restart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        const data = await response.json();
        alert(data.status);
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function runScript(scriptName) {
    const btn = event.target;
    btn.disabled = true;
    const originalText = btn.textContent;
    btn.textContent = 'Running...';

    const outputDiv = document.getElementById('script-output');
    const logDiv = document.getElementById('script-log');
    outputDiv.style.display = 'block';
    clearLog('script-log');

    addLog('script-log', `Running ${scriptName}...`, 'info');

    try {
        const response = await fetch('/api/admin/run-script', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ script: scriptName })
        });

        const data = await response.json();

        if (response.ok) {
            if (data.success) {
                addLog('script-log', 'Script completed successfully', 'success');
                if (data.stdout) {
                    data.stdout.split('\n').forEach(line => {
                        if (line.trim()) addLog('script-log', line, 'info');
                    });
                }
            } else {
                addLog('script-log', 'Script failed', 'error');
                if (data.stderr) {
                    data.stderr.split('\n').forEach(line => {
                        if (line.trim()) addLog('script-log', line, 'error');
                    });
                }
            }
        } else {
            addLog('script-log', `Error: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog('script-log', `Error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

async function runSelfHeal() {
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Running...';

    const outputDiv = document.getElementById('self-heal-output');
    const logDiv = document.getElementById('self-heal-log');
    outputDiv.style.display = 'block';
    clearLog('self-heal-log');

    addLog('self-heal-log', 'Running self-healing diagnostics...', 'info');

    try {
        const response = await fetch('/api/admin/self-heal', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        const data = await response.json();

        if (response.ok && data.repairs) {
            data.repairs.forEach(repair => {
                const type = repair.status === 'OK' ? 'success' :
                            repair.status === 'WARNING' ? 'info' : 'error';
                addLog('self-heal-log', `${repair.check}: ${repair.status}`, type);
                if (repair.action) {
                    addLog('self-heal-log', `  Action: ${repair.action}`, 'info');
                }
            });
        } else {
            addLog('self-heal-log', `Error: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog('self-heal-log', `Error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Run Auto-Repair';
    }
}

async function runDiagnostics() {
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Running...';

    const outputDiv = document.getElementById('diagnostics-output');
    const logDiv = document.getElementById('diagnostics-log');
    outputDiv.style.display = 'block';
    clearLog('diagnostics-log');

    addLog('diagnostics-log', 'Running system diagnostics...', 'info');

    try {
        const response = await fetch('/api/admin/diagnostics');
        const data = await response.json();

        if (response.ok) {
            addLog('diagnostics-log', `Database: ${data.database_status}`,
                   data.database_status === 'OK' ? 'success' : 'error');
            addLog('diagnostics-log', `Courses: ${data.courses_count}`, 'info');
            addLog('diagnostics-log', `Users: ${data.users_count}`, 'info');
            addLog('diagnostics-log', `Volume Status: ${data.volume_status}`,
                   data.volume_status === 'OK' ? 'success' : 'error');
            addLog('diagnostics-log', `Courses Directory: ${data.courses_dir}`, 'info');

            // Update diagnostics tab status
            document.getElementById('diag-db-status').textContent = data.database_status;
            document.getElementById('diag-volume-status').textContent = data.volume_status;
            document.getElementById('diag-courses-dir').textContent = data.courses_dir;
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
// USER MANAGEMENT FUNCTIONS
// ===========================

async function createUser(username, password, isAdmin) {
    try {
        const response = await fetch('/api/admin/create-user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                username: username,
                password: password,
                is_admin: isAdmin
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message);
            location.reload();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function deleteUser(userId, username) {
    if (!confirm(`Delete user '${username}'?`)) return;

    try {
        const response = await fetch('/api/admin/delete-user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ user_id: userId })
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message);
            location.reload();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

function showPasswordResetModal(userId, username) {
    document.getElementById('reset-user-id').value = userId;
    document.getElementById('reset-username').textContent = username;
    document.getElementById('reset-new-password').value = '';

    const modal = new bootstrap.Modal(document.getElementById('passwordResetModal'));
    modal.show();
}

async function confirmPasswordReset() {
    const userId = document.getElementById('reset-user-id').value;
    const newPassword = document.getElementById('reset-new-password').value;

    if (!newPassword) {
        alert('Please enter a new password');
        return;
    }

    try {
        const response = await fetch('/api/admin/reset-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                user_id: userId,
                new_password: newPassword
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message);
            bootstrap.Modal.getInstance(document.getElementById('passwordResetModal')).hide();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function seedTestUsers() {
    if (!confirm('Create 3 test users (testuser1, testuser2, testuser3)?')) return;

    try {
        const response = await fetch('/api/admin/seed-test-users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        const data = await response.json();

        if (response.ok) {
            alert(`${data.message}\nCreated: ${data.created.join(', ')}\nSkipped: ${data.skipped.join(', ')}`);
            location.reload();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// ===========================
// ABOUT CONTENT MANAGEMENT
// ===========================

async function loadAboutContent() {
    try {
        const response = await fetch('/api/admin/about-content');
        const data = await response.json();

        if (response.ok) {
            document.getElementById('about-content-editor').value = data.content || '';
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function saveAboutContent() {
    const content = document.getElementById('about-content-editor').value;

    try {
        const response = await fetch('/api/admin/about-content', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ content: content })
        });

        const data = await response.json();

        if (response.ok) {
            const msgDiv = document.getElementById('about-message');
            msgDiv.innerHTML = '<div class="alert alert-success">About content saved successfully!</div>';
            setTimeout(() => msgDiv.innerHTML = '', 3000);
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// ===========================
// INITIALIZATION
// ===========================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize CSRF token
    initCSRFToken();

    // Load initial dashboard
    loadDashboard();

    // Setup course upload
    setupCourseUpload();

    // Create user form submission
    const createUserForm = document.getElementById('create-user-form');
    if (createUserForm) {
        createUserForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('new-username').value;
            const password = document.getElementById('new-password').value;
            const isAdmin = document.getElementById('new-is-admin').checked;
            createUser(username, password, isAdmin);
        });
    }

    // Delete user buttons
    document.querySelectorAll('.delete-user-btn').forEach(button => {
        button.addEventListener('click', (event) => {
            const userId = event.target.dataset.userId;
            const username = event.target.dataset.username;
            deleteUser(userId, username);
        });
    });

    // Reset password buttons
    document.querySelectorAll('.reset-password-btn').forEach(button => {
        button.addEventListener('click', (event) => {
            const userId = event.target.dataset.userId;
            const username = event.target.dataset.username;
            showPasswordResetModal(userId, username);
        });
    });
});
