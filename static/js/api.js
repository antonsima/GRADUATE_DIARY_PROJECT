class API {
    static baseURL = '/api/';
    static authToken = localStorage.getItem('authToken');
    static refreshToken = localStorage.getItem('refreshToken');

    static async request(endpoint, options = {}) {
        const url = this.baseURL + endpoint;

        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        if (this.authToken) {
            config.headers['Authorization'] = `Bearer ${this.authToken}`;
        }

        try {
            const response = await fetch(url, config);

            if (response.status === 401 && this.refreshToken) {
                // Попытка обновить токен
                const refreshed = await this.refreshAuthToken();
                if (refreshed) {
                    // Повторяем запрос с новым токеном
                    config.headers['Authorization'] = `Bearer ${this.authToken}`;
                    return await fetch(url, config);
                }
            }

            return response;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    static async refreshAuthToken() {
        try {
            const response = await fetch('/api/auth/token/refresh/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh: this.refreshToken }),
            });

            if (response.ok) {
                const data = await response.json();
                this.setTokens(data.access, this.refreshToken);
                return true;
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
        }

        this.clearTokens();
        return false;
    }

    static setTokens(accessToken, refreshToken) {
        this.authToken = accessToken;
        this.refreshToken = refreshToken;
        localStorage.setItem('authToken', accessToken);
        localStorage.setItem('refreshToken', refreshToken);
    }

    static clearTokens() {
        this.authToken = null;
        this.refreshToken = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
    }

    // Auth methods
    static async login(email, password) {
        const response = await this.request('auth/login/', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });

        if (response.ok) {
            const data = await response.json();
            this.setTokens(data.tokens.access, data.tokens.refresh);
            return data;
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка входа');
        }
    }

    static async register(userData) {
        const response = await this.request('auth/register/', {
            method: 'POST',
            body: JSON.stringify(userData),
        });

        if (response.ok) {
            const data = await response.json();
            this.setTokens(data.tokens.access, data.tokens.refresh);
            return data;
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка регистрации');
        }
    }

    static async getProfile() {
        const response = await this.request('auth/profile/');
        if (response.ok) {
            return await response.json();
        }
        throw new Error('Ошибка получения профиля');
    }

    static async updateProfile(profileData) {
        const response = await this.request('auth/profile/', {
            method: 'PUT',
            body: JSON.stringify(profileData),
        });

        if (response.ok) {
            return await response.json();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка обновления профиля');
        }
    }

    static async logout() {
        try {
            await this.request('auth/logout/', {
                method: 'POST',
            });
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            this.clearTokens();
            window.location.href = '/';
        }
    }
}

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    // Check auth status and update UI
    updateAuthUI();

    // Login form handler
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Register form handler
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }

    // Settings form handler
    const settingsForm = document.getElementById('settingsForm');
    if (settingsForm) {
        settingsForm.addEventListener('submit', handleSettingsUpdate);
        loadProfileData();
    }

    // Profile page
    if (document.getElementById('profile-content')) {
        loadProfilePage();
    }

    // Logout buttons
    document.querySelectorAll('[data-action="logout"]').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            API.logout();
        });
    });
});

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        await API.login(email, password);
//        showMessage('Успешный вход!', 'success');
        setTimeout(() => window.location.href = '/', 1000);
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const formData = {
        email: document.getElementById('email').value,
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value,
        password: document.getElementById('password').value,
        password2: document.getElementById('password2').value
    };

    try {
        await API.register(formData);
        showMessage('Регистрация успешна!', 'success');
        setTimeout(() => window.location.href = '/', 1000);
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

async function loadProfileData() {
    try {
        const profile = await API.getProfile();
        document.getElementById('firstName').value = profile.first_name || '';
        document.getElementById('lastName').value = profile.last_name || '';
        document.getElementById('email').value = profile.email || '';
        document.getElementById('settingsForm').style.display = 'block';
        document.getElementById('loading').style.display = 'none';
    } catch (error) {
        document.getElementById('auth-required').style.display = 'block';
        document.getElementById('loading').style.display = 'none';
    }
}

async function handleSettingsUpdate(e) {
    e.preventDefault();
    const formData = {
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value,
        password: document.getElementById('password').value,
        password2: document.getElementById('password2').value
    };

    try {
        await API.updateProfile(formData);
        showMessage('Настройки сохранены!', 'success');
        // Clear password fields
        document.getElementById('password').value = '';
        document.getElementById('password2').value = '';
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

async function loadProfilePage() {
    try {
        const profile = await API.getProfile();
        document.getElementById('user-name').textContent = `${profile.first_name} ${profile.last_name}`;
        document.getElementById('user-email').textContent = profile.email;

        // Load statistics (you'll need to implement these endpoints)
        // const stats = await API.request('dashboard/');
        // document.getElementById('total-entries').textContent = stats.total_entries || 0;
        // document.getElementById('monthly-entries').textContent = stats.monthly_entries || 0;

        document.getElementById('profile-content').style.display = 'block';
        document.getElementById('loading').style.display = 'none';
    } catch (error) {
        document.getElementById('auth-required').style.display = 'block';
        document.getElementById('loading').style.display = 'none';
    }
}

function updateAuthUI() {
    const authLinks = document.getElementById('auth-links');
    const profileLinks = document.getElementById('profile-links');

    if (API.authToken) {
        if (authLinks) authLinks.classList.add('d-none');
        if (profileLinks) profileLinks.classList.remove('d-none');
    } else {
        if (authLinks) authLinks.classList.remove('d-none');
        if (profileLinks) profileLinks.classList.add('d-none');
    }
}

function showMessage(message, type) {
    // Implement message display logic
    alert(`${type}: ${message}`);
}