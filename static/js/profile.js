// --- CSRF Token Helper (inline copy from main.js) ---
// This is duplicated here to avoid module loading issues with browser caching
let CSRF_TOKEN = null;

async function getCsrfToken() {
    if (CSRF_TOKEN) return CSRF_TOKEN;

    try {
        const response = await fetch('/csrf-token', { method: 'GET' });
        if (!response.ok) {
            throw new Error(`Failed to fetch CSRF token: ${response.status}`);
        }
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

    // Add CSRF token to headers for state-changing requests
    if (['POST', 'PUT', 'DELETE', 'PATCH'].includes((options.method || 'GET').toUpperCase())) {
        fetchOptions.headers = {
            ...fetchOptions.headers,
            'X-CSRFToken': CSRF_TOKEN || ''
        };
    }

    return fetch(url, fetchOptions);
}
// --- End CSRF Token Helper ---

document.addEventListener('DOMContentLoaded', init);

async function init() {
    // Ensure CSRF token is loaded first
    await getCsrfToken();

    // Logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            await fetchWithCsrf('/api/logout', { method: 'POST' });
            window.location.href = '/';
        });
    }

    // Load profile data (don't let this block initialization)
    try {
        await loadProfile();
    } catch (error) {
        console.error('Failed to load profile during init:', error);
        // Continue with initialization even if profile loading fails
    }

    // Edit profile modal handlers
    setupProfileEditor();

    // Password change modal handlers
    setupPasswordChange();
}

async function loadProfile() {
    try {
        const response = await fetch('/api/profile');
        if (!response.ok) throw new Error('Failed to load profile');

        const data = await response.json();

        // Update profile sidebar
        document.getElementById('avatar-img').src = data.user.avatar;
        document.getElementById('profile-username').textContent = data.user.username;
        document.getElementById('profile-pronouns').textContent = data.user.pronouns || '';
        document.getElementById('profile-about').textContent = data.user.about_me || 'No bio yet. Click "Edit Profile" to add one!';

        if (data.user.created_at) {
            const joinedDate = new Date(data.user.created_at);
            document.getElementById('profile-joined').textContent = `Joined ${joinedDate.toLocaleDateString()}`;
        }

        // Courses in Progress
        const inProgressDiv = document.getElementById('courses-in-progress');
        if (data.courses_in_progress.length > 0) {
            inProgressDiv.innerHTML = '<div class="list-group">' +
                data.courses_in_progress.map(course => `
                    <a href="/course/${course.uid}" class="list-group-item list-group-item-action">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">${course.title}</h6>
                            <small class="text-muted">${course.status}</small>
                        </div>
                    </a>
                `).join('') +
                '</div>';
        } else {
            inProgressDiv.innerHTML = '<p class="text-muted">No courses in progress</p>';
        }

        // Completed Courses
        const completedDiv = document.getElementById('courses-completed');
        if (data.courses_completed.length > 0) {
            completedDiv.innerHTML = '<div class="list-group">' +
                data.courses_completed.map(course => `
                    <a href="/course/${course.uid}" class="list-group-item list-group-item-action">
                        <h6 class="mb-1">${course.title}</h6>
                    </a>
                `).join('') +
                '</div>';
        } else {
            completedDiv.innerHTML = '<p class="text-muted">No completed courses yet</p>';
        }

        // Reading List
        const readingDiv = document.getElementById('reading-list');
        if (data.reading_list.length > 0) {
            readingDiv.innerHTML = '<div class="list-group">' +
                data.reading_list.map(book => `
                    <a href="/reader/${book.uid}" class="list-group-item list-group-item-action">
                        <div class="d-flex w-100 justify-content-between align-items-center">
                            <h6 class="mb-1">${book.title}</h6>
                            <div class="progress" style="width: 100px;">
                                <div class="progress-bar" role="progressbar" style="width: ${book.progress}%">${book.progress}%</div>
                            </div>
                        </div>
                    </a>
                `).join('') +
                '</div>';
        } else {
            readingDiv.innerHTML = '<p class="text-muted">No books in reading list</p>';
        }

        // Notes List
        const notesDiv = document.getElementById('notes-list');
        if (data.notes.length > 0) {
            notesDiv.innerHTML = '<div class="list-group">' +
                data.notes.map(note => {
                    if (note.type === 'course') {
                        return `
                            <a href="/course/${note.course_uid}" class="list-group-item list-group-item-action">
                                <h6 class="mb-1">${note.course_title}</h6>
                                <p class="mb-1 small text-muted">${note.content}</p>
                            </a>
                        `;
                    } else if (note.type === 'ebook') {
                        return `
                            <a href="/textbook/${note.ebook_id}" class="list-group-item list-group-item-action">
                                <h6 class="mb-1">${note.ebook_title} <span class="badge bg-secondary">Book</span></h6>
                                <p class="mb-1 small text-muted">${note.content}</p>
                            </a>
                        `;
                    }
                    return '';
                }).join('') +
                '</div>';
        } else {
            notesDiv.innerHTML = '<p class="text-muted">No notes yet</p>';
        }

    } catch (error) {
        console.error('Failed to load profile:', error);
    }
}

function setupProfileEditor() {
    const editModal = document.getElementById('editProfileModal');
    const saveBtn = document.getElementById('save-profile-btn');
    const avatarUpload = document.getElementById('avatar-upload');
    const pronounsSelect = document.getElementById('edit-pronouns');
    const customPronounsWrapper = document.getElementById('custom-pronouns-wrapper');

    // Show custom pronouns input when "custom" is selected
    pronounsSelect.addEventListener('change', () => {
        if (pronounsSelect.value === 'custom') {
            customPronounsWrapper.style.display = 'block';
        } else {
            customPronounsWrapper.style.display = 'none';
        }
    });

    // When modal opens, populate current values
    editModal.addEventListener('show.bs.modal', async () => {
        const response = await fetch('/api/profile');
        const data = await response.json();

        document.getElementById('edit-about').value = data.user.about_me || '';
        document.getElementById('edit-gender').value = data.user.gender || '';

        // Handle pronouns
        const pronouns = data.user.pronouns || '';
        const standardPronouns = ['he/him', 'she/her', 'they/them'];
        if (standardPronouns.includes(pronouns)) {
            pronounsSelect.value = pronouns;
        } else if (pronouns) {
            pronounsSelect.value = 'custom';
            document.getElementById('edit-pronouns-custom').value = pronouns;
            customPronounsWrapper.style.display = 'block';
        } else {
            pronounsSelect.value = '';
        }
    });

    // Save profile
    saveBtn.addEventListener('click', async () => {
        const errorDiv = document.getElementById('edit-error');
        errorDiv.style.display = 'none';

        try {
            // Upload avatar if selected
            if (avatarUpload.files.length > 0) {
                const formData = new FormData();
                formData.append('avatar', avatarUpload.files[0]);

                const uploadResponse = await fetchWithCsrf('/api/profile/avatar', {
                    method: 'POST',
                    body: formData
                });

                if (!uploadResponse.ok) {
                    const error = await uploadResponse.json();
                    throw new Error(error.error || 'Avatar upload failed');
                }
            }

            // Get pronouns value
            let pronounsValue = pronounsSelect.value;
            if (pronounsValue === 'custom') {
                pronounsValue = document.getElementById('edit-pronouns-custom').value;
            }

            // Update profile data
            const profileData = {
                about_me: document.getElementById('edit-about').value,
                gender: document.getElementById('edit-gender').value,
                pronouns: pronounsValue
            };

            const response = await fetchWithCsrf('/api/profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(profileData)
            });

            if (!response.ok) throw new Error('Failed to update profile');

            // Close modal and reload profile
            bootstrap.Modal.getInstance(editModal).hide();
            await loadProfile();

        } catch (error) {
            errorDiv.textContent = error.message;
            errorDiv.style.display = 'block';
        }
    });
}

function setupPasswordChange() {
    const passwordModal = document.getElementById('changePasswordModal');
    const savePasswordBtn = document.getElementById('save-password-btn');
    const passwordForm = document.getElementById('change-password-form');
    const currentPasswordInput = document.getElementById('current-password');
    const newPasswordInput = document.getElementById('new-password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    const errorDiv = document.getElementById('password-error');
    const successDiv = document.getElementById('password-success');

    // Reset form when modal opens
    passwordModal.addEventListener('show.bs.modal', () => {
        passwordForm.reset();
        errorDiv.style.display = 'none';
        successDiv.style.display = 'none';
    });

    // Handle password change
    savePasswordBtn.addEventListener('click', async () => {
        errorDiv.style.display = 'none';
        successDiv.style.display = 'none';

        const currentPassword = currentPasswordInput.value;
        const newPassword = newPasswordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        // Client-side validation
        if (!currentPassword || !newPassword || !confirmPassword) {
            errorDiv.textContent = 'All fields are required';
            errorDiv.style.display = 'block';
            return;
        }

        if (newPassword.length < 6) {
            errorDiv.textContent = 'New password must be at least 6 characters long';
            errorDiv.style.display = 'block';
            return;
        }

        if (newPassword !== confirmPassword) {
            errorDiv.textContent = 'New passwords do not match';
            errorDiv.style.display = 'block';
            return;
        }

        try {
            const response = await fetchWithCsrf('/api/profile/change-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword,
                    confirm_password: confirmPassword
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to change password');
            }

            // Success!
            successDiv.textContent = 'Password changed successfully! You can now use your new password to login.';
            successDiv.style.display = 'block';
            passwordForm.reset();

            // Close modal after 2 seconds
            setTimeout(() => {
                bootstrap.Modal.getInstance(passwordModal).hide();
            }, 2000);

        } catch (error) {
            errorDiv.textContent = error.message;
            errorDiv.style.display = 'block';
        }
    });
}
