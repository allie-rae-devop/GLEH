// --- CSRF Token Helper (inline copy from main.js) ---
let CSRF_TOKEN = null;

async function getCsrfToken() {
  if (CSRF_TOKEN) return CSRF_TOKEN;
  try {
    const response = await fetch('/csrf-token', { method: 'GET' });
    const data = await response.json();
    CSRF_TOKEN = data.csrf_token;
    return CSRF_TOKEN;
  } catch (error) {
    console.error('Failed to get CSRF token:', error);
    return null;
  }
}

function fetchWithCsrf(url, options = {}) {
  const fetchOptions = { ...options };
  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes((options.method || 'GET').toUpperCase())) {
    fetchOptions.headers = {
      ...fetchOptions.headers,
      'X-CSRFToken': CSRF_TOKEN || ''
    };
  }
  return fetch(url, fetchOptions);
}

document.addEventListener('DOMContentLoaded', init);

async function init() {
    // Ensure CSRF token is loaded first
    await getCsrfToken();
    await checkSession();

    const saveBtn = document.getElementById('save-note-btn');
    const noteContent = document.getElementById('note-content');

    if (saveBtn) {
        const courseUid = saveBtn.dataset.courseUid;

        // Load note and progress
        await loadNote(courseUid);
        await loadProgress(courseUid);

        // Setup event listeners
        saveBtn.addEventListener('click', () => saveNote(courseUid));
        setupProgressButtons(courseUid);
    }

    // Setup auth modal handlers
    setupAuthHandlers();
}

async function checkSession() {
    const authContainer = document.getElementById('auth-container');
    if (!authContainer) return;

    try {
        const response = await fetch('/api/check_session');
        if (!response.ok) throw new Error('Not authenticated');
        const data = await response.json();

        authContainer.innerHTML = `
            <span class='text-white me-2'>Welcome, ${data.user.username}</span>
            <button id='logout-btn' class='btn btn-sm btn-outline-secondary'>Logout</button>
        `;

        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', async () => {
                await fetchWithCsrf('/api/logout', { method: 'POST' });
                window.location.reload();
            });
        }
    } catch (error) {
        authContainer.innerHTML = `
            <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#auth-modal">
                Login / Register
            </button>
        `;
    }
}

function setupAuthHandlers() {
    const loginBtn = document.getElementById('auth-login-btn');
    const registerBtn = document.getElementById('auth-register-btn');
    const authModal = document.getElementById('auth-modal');

    if (loginBtn) loginBtn.addEventListener('click', login);
    if (registerBtn) registerBtn.addEventListener('click', register);
}

async function login() {
    const username = document.getElementById('auth-username').value;
    const password = document.getElementById('auth-password').value;
    const authError = document.getElementById('auth-error');

    try {
        const response = await fetchWithCsrf('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Login failed');

        // Close modal and reload page
        const modalEl = document.getElementById('auth-modal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
        window.location.reload();
    } catch (error) {
        authError.textContent = error.message;
        authError.style.display = 'block';
    }
}

async function register() {
    const username = document.getElementById('auth-username').value;
    const password = document.getElementById('auth-password').value;
    const authError = document.getElementById('auth-error');

    try {
        const response = await fetchWithCsrf('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Registration failed');

        // Auto-login after registration
        await login();
    } catch (error) {
        authError.textContent = error.message;
        authError.style.display = 'block';
    }
}

async function loadNote(courseUid) {
    const noteContent = document.getElementById('note-content');
    if (!noteContent) return;

    try {
        const response = await fetch(`/api/course/${courseUid}/note`);
        if (!response.ok) return;

        const data = await response.json();
        noteContent.value = data.content || '';
    } catch (error) {
        console.error('Failed to load note:', error);
    }
}

async function saveNote(courseUid) {
    const noteContent = document.getElementById('note-content');
    const statusDiv = document.getElementById('note-status');

    try {
        const response = await fetchWithCsrf('/api/course/note', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ course_uid: courseUid, content: noteContent.value }),
        });

        if (response.ok) {
            statusDiv.textContent = 'Note saved successfully!';
            statusDiv.className = 'mt-2 text-success small';
            setTimeout(() => statusDiv.textContent = '', 3000);
        } else {
            throw new Error('Failed to save note');
        }
    } catch (error) {
        console.error('Failed to save note:', error);
        statusDiv.textContent = 'Error saving note. Please try again.';
        statusDiv.className = 'mt-2 text-danger small';
    }
}

async function loadProgress(courseUid) {
    const currentStatusSpan = document.getElementById('current-status');
    if (!currentStatusSpan) return;

    try {
        const response = await fetch('/api/content');
        if (!response.ok) return;

        const data = await response.json();
        const course = data.content.find(c => c.uid === courseUid);

        if (course && course.user_progress) {
            updateProgressUI(course.user_progress);
        } else {
            updateProgressUI('Not Started');
        }
    } catch (error) {
        console.error('Failed to load progress:', error);
        updateProgressUI('Not Started');
    }
}

function updateProgressUI(status) {
    const currentStatusSpan = document.getElementById('current-status');
    if (currentStatusSpan) {
        currentStatusSpan.textContent = status;
    }

    // Update circular indicators
    const circles = document.querySelectorAll('.progress-circle');

    if (status === 'Not Started') {
        // Reset both circles to inactive
        circles.forEach(circle => {
            circle.style.opacity = '0.6';
            circle.classList.remove('active');
        });
    } else {
        circles.forEach(circle => {
            const circleStatus = circle.dataset.status;

            if (circleStatus === status) {
                // Active: fully opaque
                circle.style.opacity = '1';
                circle.classList.add('active');
            } else {
                // Inactive: 60% transparent
                circle.style.opacity = '0.6';
                circle.classList.remove('active');
            }
        });
    }
}

function setupProgressButtons(courseUid) {
    const circles = document.querySelectorAll('.progress-circle');

    circles.forEach(circle => {
        circle.addEventListener('click', async () => {
            const clickedStatus = circle.dataset.status;
            const currentStatusText = document.getElementById('current-status').textContent;
            let newStatus;

            // Toggle behavior
            if (currentStatusText === clickedStatus) {
                // Clicking the active one turns it off
                newStatus = 'Not Started';
            } else {
                // Clicking inactive one activates it (and deactivates the other)
                newStatus = clickedStatus;
            }

            await updateProgress(courseUid, newStatus);
        });
    });
}

async function updateProgress(courseUid, status) {
    try {
        const response = await fetchWithCsrf('/api/course/progress', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ course_uid: courseUid, status }),
        });

        if (response.ok) {
            updateProgressUI(status);
        } else {
            alert('Error updating progress. Please make sure you are logged in.');
        }
    } catch (error) {
        console.error('Failed to update progress:', error);
        alert('An error occurred while updating progress.');
    }
}
