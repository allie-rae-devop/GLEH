/**
 * Delays invoking a function until after 'delay' ms have passed.
 */
function debounce(func, delay) {
  let timeout;
  return function(...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), delay);
  };
}

// --- CSRF Token Helper ---
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

  // Only add CSRF token for state-changing requests
  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes((options.method || 'GET').toUpperCase())) {
    fetchOptions.headers = {
      ...fetchOptions.headers,
      'X-CSRFToken': CSRF_TOKEN || ''
    };
  }

  return fetch(url, fetchOptions);
}

// Make CSRF functions globally available for other scripts
window.getCsrfToken = getCsrfToken;
window.fetchWithCsrf = fetchWithCsrf;

// --- HTML Template Functions (Moved to top for global accessibility) ---
function createCourseCard(course) {
  const coursePageUrl = `/course/${course.uid}`;
  const progress = course.user_progress || 'Not Started';
  let badge = '';
  if (progress === 'In Progress') {
    badge = '<span class="badge bg-warning text-dark">In Progress</span>';
  } else if (progress === 'Completed') {
    badge = '<span class="badge bg-success">Completed</span>';
  } else {
    badge = '<span class="badge bg-secondary">Not Started</span>';
  }

  return `
  <div class="col">
    <div class="card h-100 shadow-sm" style="background-color: var(--bs-tertiary-bg); position: relative;">
      <a href="${coursePageUrl}" class="text-decoration-none">
        <img src="${course.thumbnail}" class="card-img-top" alt="${course.title} thumbnail" style="aspect-ratio: 16/9; object-fit: cover;">
      </a>
      <div style="position: absolute; top: 10px; right: 10px;">${badge}</div>
      <div class="card-body d-flex flex-column">
        <h5 class="card-title fs-6">
          <a href="${coursePageUrl}" class="text-decoration-none text-body">${course.title}</a>
        </h5>
        <p class="card-text small text-body-secondary flex-grow-1">${course.description || ''}</p>
        <div class="mt-auto">
            <a href="${coursePageUrl}" class="btn btn-primary btn-sm w-100">View Details</a>
        </div>
      </div>
    </div>
  </div>
  `;
}

function createEbookCard(ebook) {
  return `
  <div class="col">
    <a href="${ebook.path}" class="card-ebook-link" title="${ebook.title}">
      <img src="${ebook.cover_path}"
           class="img-fluid rounded shadow-sm ebook-cover"
           alt="${ebook.title} cover"
           style="aspect-ratio: 2/3; object-fit: cover; width: 100%; min-height: 200px; background-color: #f0f0f0;"
           onerror="this.src='/static/images/default-book.jpg'">
    </a>
  </div>
  `;
}

function createCourseRow(course) {
  const coursePageUrl = `/course/${course.uid}`;
  const progress = course.user_progress || 'Not Started';
  let badge = '';
  if (progress === 'In Progress') {
    badge = '<span class="badge bg-warning text-dark">In Progress</span>';
  } else if (progress === 'Completed') {
    badge = '<span class="badge bg-success">Completed</span>';
  } else {
    badge = '<span class="badge bg-secondary">Not Started</span>';
  }

  return `
  <tr>
    <td style="width: 150px;">
      <a href="${coursePageUrl}">
        <img src="${course.thumbnail}" class="img-fluid rounded" alt="${course.title} thumbnail">
      </a>
    </td>
    <td>
      <div class="minimal-card d-flex justify-content-between align-items-center">
        <div>
          <h5 class="card-title mb-1">
            <a href="${coursePageUrl}" class="text-decoration-none text-body">${course.title}</a>
          </h5>
        </div>
        <div>${badge}</div>
      </div>
    </td>
  </tr>
  `;
}

function createEbookRow(ebook) {
  return `
  <tr>
    <td style="width: 120px; text-align: center;">
      <a href="${ebook.path}" class="card-ebook-link" title="${ebook.title}">
        <img src="${ebook.cover_path}"
             class="img-fluid rounded shadow-sm ebook-cover"
             alt="${ebook.title} cover"
             style="width: 100px; height: 150px; object-fit: cover; display: block; margin: 0 auto;"
             onerror="this.src='/static/images/default-book.jpg'">
      </a>
    </td>
    <td>
      <div class="minimal-card">
        <h5 class="card-title">
          <a href="${ebook.path}" class="text-decoration-none text-body">${ebook.title}</a>
        </h5>
      </div>
    </td>
  </tr>
  `;
}

// --- Application State ---
let MASTER_DATA = [];
let IS_AUTHENTICATED = false;
let CURRENT_VIEW = 'dashboard';
let PAGINATION_STATE = { library: { currentPage: 1, itemsPerPage: 12 } };
let CURRENT_FILTERS = { searchTerm: '', categories: new Set(), type: 'all' };

// --- Main Initialization ---
document.addEventListener('DOMContentLoaded', init);

// --- Function Definitions ---

async function login() {
    const authUsername = document.getElementById('auth-username');
    const authPassword = document.getElementById('auth-password');
    const authError = document.getElementById('auth-error');
    const authModalEl = document.getElementById('auth-modal');
    const authModal = authModalEl ? bootstrap.Modal.getInstance(authModalEl) : null;

    try {
        const response = await fetchWithCsrf('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: authUsername.value, password: authPassword.value }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Login failed');

        if (authModal) authModal.hide();
        await checkSession();
        await fetchContent();
    } catch (error) {
        if (authError) {
            authError.textContent = error.message;
            authError.style.display = 'block';
        }
    }
}

async function register() {
    const authUsername = document.getElementById('auth-username');
    const authPassword = document.getElementById('auth-password');
    const authError = document.getElementById('auth-error');
    try {
        const response = await fetchWithCsrf('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: authUsername.value, password: authPassword.value }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Registration failed');
        await login();
    } catch (error) {
        if (authError) {
            authError.textContent = error.message;
            authError.style.display = 'block';
        }
    }
}

async function logout() {
    await fetchWithCsrf('/api/logout', { method: 'POST' });
    window.location.reload();
}

async function checkSession() {
    const authContainer = document.getElementById('auth-container');
    const navbarNav = document.querySelector('#navbarNav .navbar-nav');
    if (!authContainer) return;

    try {
        const response = await fetch('/api/check_session');
        if (!response.ok) throw new Error('Not authenticated');
        const data = await response.json();

        IS_AUTHENTICATED = true;
        authContainer.innerHTML = `<span class='text-white'>Welcome, ${data.user.username}</span><button id='logout-btn' class='btn btn-sm btn-outline-secondary ms-2'>Logout</button>`;
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) logoutBtn.addEventListener('click', logout);

        // Add Profile link if authenticated
        if (navbarNav) {
            // Remove old profile/admin links if they exist
            const oldProfile = navbarNav.querySelector('.profile-link');
            const oldAdmin = navbarNav.querySelector('.admin-link');
            if (oldProfile) oldProfile.remove();
            if (oldAdmin) oldAdmin.remove();

            // Add Profile link
            const profileLi = document.createElement('li');
            profileLi.className = 'nav-item profile-link';
            profileLi.innerHTML = '<a class="nav-link" href="/profile">Profile</a>';
            navbarNav.appendChild(profileLi);

            // Add Admin link if user is admin
            if (data.user.is_admin) {
                const adminLi = document.createElement('li');
                adminLi.className = 'nav-item admin-link';
                adminLi.innerHTML = '<a class="nav-link" href="/admin">Admin</a>';
                navbarNav.appendChild(adminLi);
            }
        }
    } catch (error) {
        IS_AUTHENTICATED = false;
        authContainer.innerHTML = `<button id="login-show-btn" class="btn btn-primary btn-sm text-nowrap">Login / Register</button>`;
        const loginShowBtn = document.getElementById('login-show-btn');
        if (loginShowBtn) {
            loginShowBtn.addEventListener('click', () => {
                const authModalEl = document.getElementById('auth-modal');
                if (authModalEl) new bootstrap.Modal(authModalEl).show();
            });
        }

        // Remove Profile/Admin links when not authenticated
        if (navbarNav) {
            const oldProfile = navbarNav.querySelector('.profile-link');
            const oldAdmin = navbarNav.querySelector('.admin-link');
            if (oldProfile) oldProfile.remove();
            if (oldAdmin) oldAdmin.remove();
        }
    }
    renderContent();
}

async function fetchContent() {
    try {
        const response = await fetch('/api/content');
        if (!response.ok) throw new Error('Failed to fetch content');
        const data = await response.json();
        MASTER_DATA = data.content;

        populateCategoryFilters(MASTER_DATA);
        renderContent();
    } catch (error) {
        console.error('Failed to fetch content:', error);
        const courseTableBody = document.getElementById('course-table-body');
        if (courseTableBody) courseTableBody.innerHTML = '<tr><td colspan="2"><p class="text-danger">Could not load content.</p></td></tr>';
    }
}

function attachAppEventListeners() {
    window.addEventListener('hashchange', handleRouteChange);

    // Handle initial route based on current hash (hashchange doesn't fire on page load)
    handleRouteChange();

    const searchBar = document.getElementById('search-bar');
    if (searchBar) {
        searchBar.addEventListener('keyup', debounce(event => {
            CURRENT_FILTERS.searchTerm = event.target.value.toLowerCase().trim();
            renderContent();
        }, 300));
    }

    const typeFilterWrapper = document.getElementById('type-filter-wrapper');
    if (typeFilterWrapper) {
        typeFilterWrapper.addEventListener('click', event => {
            if (event.target.matches('.type-filter-item')) {
                event.preventDefault();
                CURRENT_FILTERS.type = event.target.dataset.type;
                renderContent();
            }
        });
    }

    const categoryFilterWrapper = document.getElementById('category-filter-wrapper');
    if (categoryFilterWrapper) {
        categoryFilterWrapper.addEventListener('click', event => {
            if (event.target.matches('.category-checkbox')) {
                const checkbox = event.target;
                const category = checkbox.value;
                checkbox.checked ? CURRENT_FILTERS.categories.add(category) : CURRENT_FILTERS.categories.delete(category);
                renderContent();
            }
        });
    }

    const libraryPagination = document.getElementById('library-pagination');
    if(libraryPagination) {
        libraryPagination.addEventListener('click', event => {
            if (event.target.matches('.page-link')) {
                event.preventDefault();
                const newPage = parseInt(event.target.dataset.page, 10);
                if (newPage) {
                    PAGINATION_STATE.library.currentPage = newPage;
                    renderContent();
                }
            }
        });
    }
}

function handleRouteChange() {
    const hash = window.location.hash;
    if (hash === '#courses') {
        CURRENT_VIEW = 'courses';
    } else if (hash === '#ebooks') {
        CURRENT_VIEW = 'ebooks';
    } else {
        CURRENT_VIEW = 'dashboard';
    }
    renderContent();
}

function populateCategoryFilters(content) {
  const categoryFilterWrapper = document.getElementById('category-filter-wrapper');
  if (!categoryFilterWrapper) return;

  const allCategories = content.flatMap(item => item.categories);
  const uniqueCategories = [...new Set(allCategories)].sort();

  let dropdownHtml = `
    <button class="btn btn-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" data-bs-auto-close="outside" aria-expanded="false">
      Filter by Category
    </button>
    <ul class="dropdown-menu" aria-labelledby="category-filter-btn">
  `;

  for (const category of uniqueCategories) {
    const isChecked = CURRENT_FILTERS.categories.has(category) ? 'checked' : '';
    dropdownHtml += `
    <li>
      <a class="dropdown-item" href="#">
        <input type="checkbox" class="form-check-input category-checkbox me-2" value="${category}" id="cat-${category}" ${isChecked}>
        <label class="form-check-label" for="cat-${category}">${category}</label>
      </a>
    </li>
    `;
  }
  dropdownHtml += '</ul>';
  categoryFilterWrapper.innerHTML = dropdownHtml;
}

function getFilteredContent() {
  const { searchTerm, categories, type } = CURRENT_FILTERS;
  const activeCategories = Array.from(categories);

  if (!Array.isArray(MASTER_DATA)) return [];

  return MASTER_DATA.filter(item => {
    const matchesType = type === 'all' || item.type === type;

    const matchesSearch = searchTerm === '' ||
      item.title.toLowerCase().includes(searchTerm) ||
      (item.description || '').toLowerCase().includes(searchTerm) ||
      item.categories.some(cat => cat.toLowerCase().includes(searchTerm));

    const matchesCategories = activeCategories.length === 0 ||
      activeCategories.every(cat => item.categories.includes(cat));

    return matchesType && matchesSearch && matchesCategories;
  });
}

function renderPagination(container, totalItems, state) {
    if (!container) return;
    container.innerHTML = '';
    const totalPages = Math.ceil(totalItems / state.itemsPerPage);
    if (totalPages <= 1) return;

    // ... pagination logic
}

function renderDashboard() {
    const courseTableBody = document.getElementById('course-table-body');
    const ebookTableBody = document.getElementById('ebook-table-body');
    if (!courseTableBody || !ebookTableBody) return;

    const courses = MASTER_DATA.filter(item => item.type === 'course');
    const ebooks = MASTER_DATA.filter(item => item.type === 'ebook');

    const coursesToShow = courses.sort(() => 0.5 - Math.random()).slice(0, 6);
    courseTableBody.innerHTML = '';
    if (coursesToShow.length > 0) {
        coursesToShow.forEach(course => courseTableBody.insertAdjacentHTML('beforeend', createCourseRow(course)));
    } else {
        courseTableBody.innerHTML = '<tr><td colspan="2" class="text-center text-muted">No courses match your criteria.</td></tr>';
    }

    const ebooksToShow = ebooks.sort(() => 0.5 - Math.random()).slice(0, 6);
    ebookTableBody.innerHTML = '';
    if (ebooksToShow.length > 0) {
        ebooksToShow.forEach(ebook => ebookTableBody.insertAdjacentHTML('beforeend', createEbookRow(ebook)));
    } else {
        ebookTableBody.innerHTML = '<tr><td colspan="2" class="text-center text-muted">No textbooks match your criteria.</td></tr>';
    }
}

function renderLibraryView() {
    const libraryGrid = document.getElementById('library-grid');
    const libraryTitle = document.getElementById('library-title');
    const libraryPagination = document.getElementById('library-pagination');
    if (!libraryGrid || !libraryTitle) return;

    const viewType = CURRENT_VIEW.slice(0, -1);
    // Filter by the current view type (course or ebook)
    const filteredContent = getFilteredContent().filter(item => item.type === viewType);

    libraryTitle.textContent = `Full ${viewType.charAt(0).toUpperCase() + viewType.slice(1)} Library`;

    // Show all items without pagination
    libraryGrid.innerHTML = '';
    if (filteredContent.length > 0) {
        filteredContent.forEach(item => {
            const cardHtml = item.type === 'course' ? createCourseCard(item) : createEbookCard(item);
            libraryGrid.insertAdjacentHTML('beforeend', cardHtml);
        });
    } else {
        libraryGrid.innerHTML = '<p class="text-body-secondary">No items match your criteria.</p>';
    }

    // Hide pagination since we're showing all items
    if (libraryPagination) {
        libraryPagination.style.display = 'none';
    }
}

function renderContent() {
    const dashboardView = document.getElementById('dashboard-view');
    const libraryView = document.getElementById('library-view');
    const filterContainer = document.getElementById('filter-container');
    const typeFilterWrapper = document.getElementById('type-filter-wrapper');
    if (!dashboardView || !libraryView || !filterContainer) return;

    const isDashboard = CURRENT_VIEW === 'dashboard';

    dashboardView.style.display = isDashboard ? '' : 'none';
    libraryView.style.display = isDashboard ? 'none' : '';
    filterContainer.style.display = isDashboard ? 'none' : '';

    // Hide type filter on library views since each page is type-specific
    if (typeFilterWrapper) {
        typeFilterWrapper.style.display = isDashboard ? '' : 'none';
    }

    if (isDashboard) {
        renderDashboard();
    } else {
        renderLibraryView();
    }
}

async function init() {
    const authLoginBtn = document.getElementById('auth-login-btn');
    const authRegisterBtn = document.getElementById('auth-register-btn');
    const authPassword = document.getElementById('auth-password');

    // Get CSRF token first (required for all state-changing requests)
    await getCsrfToken();

    if (authLoginBtn) authLoginBtn.addEventListener('click', login);
    if (authRegisterBtn) authRegisterBtn.addEventListener('click', register);

    // Allow Enter key to submit login form
    if (authPassword) {
        authPassword.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                login();
            }
        });
    }

    attachAppEventListeners();

    await Promise.all([
        fetchContent(),
        checkSession()
    ]);
}
