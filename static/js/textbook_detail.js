// Textbook Detail Page - Note saving functionality

// CSRF token fetching
async function getCSRFToken() {
    try {
        const response = await fetch('/csrf-token');
        if (!response.ok) throw new Error('Failed to fetch CSRF token');
        const data = await response.json();
        return data.csrf_token;
    } catch (error) {
        console.error('Error fetching CSRF token:', error);
        return null;
    }
}

//Save note button
document.addEventListener('DOMContentLoaded', () => {
    const saveNoteBtn = document.getElementById('save-note-btn');
    const noteContent = document.getElementById('note-content');
    const noteStatus = document.getElementById('note-status');

    if (saveNoteBtn && noteContent) {
        saveNoteBtn.addEventListener('click', async () => {
            const bookId = saveNoteBtn.dataset.bookId;
            const content = noteContent.value;

            try {
                const csrfToken = await getCSRFToken();
                if (!csrfToken) {
                    noteStatus.textContent = 'Error: Could not get CSRF token';
                    noteStatus.style.color = 'red';
                    return;
                }

                const response = await fetch('/api/textbook/note', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        book_id: bookId,
                        content: content
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    noteStatus.textContent = data.message || 'Note saved successfully!';
                    noteStatus.style.color = 'green';
                    setTimeout(() => {
                        noteStatus.textContent = '';
                    }, 3000);
                } else {
                    noteStatus.textContent = 'Error: ' + (data.error || 'Failed to save note');
                    noteStatus.style.color = 'red';
                }
            } catch (error) {
                console.error('Error saving note:', error);
                noteStatus.textContent = 'Error: Could not save note';
                noteStatus.style.color = 'red';
            }
        });
    }

    // Authentication handling (similar to main.js)
    const authContainer = document.getElementById('auth-container');
    const authModal = new bootstrap.Modal(document.getElementById('auth-modal'));
    const authLoginBtn = document.getElementById('auth-login-btn');
    const authRegisterBtn = document.getElementById('auth-register-btn');
    const authUsernameInput = document.getElementById('auth-username');
    const authPasswordInput = document.getElementById('auth-password');
    const authError = document.getElementById('auth-error');

    // Check session on page load
    fetch('/api/check_session')
        .then(response => response.json())
        .then(data => {
            if (data.logged_in) {
                authContainer.innerHTML = `
                    <span class="text-light me-3">Hello, ${data.username}${data.is_admin ? ' (Admin)' : ''}</span>
                    <button id="logout-btn" class="btn btn-outline-light btn-sm">Logout</button>
                `;
                document.getElementById('logout-btn').addEventListener('click', () => {
                    fetch('/api/logout', { method: 'POST' })
                        .then(() => window.location.reload());
                });
            } else {
                authContainer.innerHTML = '<button id="login-btn" class="btn btn-outline-light btn-sm">Login</button>';
                document.getElementById('login-btn').addEventListener('click', () => authModal.show());
            }
        });

    // Login handler
    if (authLoginBtn) {
        authLoginBtn.addEventListener('click', async () => {
            const username = authUsernameInput.value;
            const password = authPasswordInput.value;

            try {
                const csrfToken = await getCSRFToken();
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (response.ok) {
                    window.location.reload();
                } else {
                    authError.textContent = data.error;
                    authError.style.display = 'block';
                }
            } catch (error) {
                authError.textContent = 'An error occurred. Please try again.';
                authError.style.display = 'block';
            }
        });
    }

    // Register handler
    if (authRegisterBtn) {
        authRegisterBtn.addEventListener('click', async () => {
            const username = authUsernameInput.value;
            const password = authPasswordInput.value;

            try {
                const csrfToken = await getCSRFToken();
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (response.ok) {
                    window.location.reload();
                } else {
                    authError.textContent = data.error;
                    authError.style.display = 'block';
                }
            } catch (error) {
                authError.textContent = 'An error occurred. Please try again.';
                authError.style.display = 'block';
            }
        });
    }
});
