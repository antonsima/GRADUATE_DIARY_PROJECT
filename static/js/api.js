// Функция для получения CSRF-токена из cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Функции для работы с localStorage
function saveTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    updateAuthStatus();
}

function getAccessToken() {
    return localStorage.getItem('access_token');
}

function getRefreshToken() {
    return localStorage.getItem('refresh_token');
}

function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    updateAuthStatus();
}

// Функция для API запросов
async function apiRequest(url, method, data, includeAuth = true) {
    console.log(`API Request: ${method} ${url}`, data);

    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    };

    // Добавляем body только если есть данные
    if (data) {
        options.body = JSON.stringify(data);
    }

    if (includeAuth) {
        const token = localStorage.getItem('access_token');
        console.log('Токен для авторизации:', token);
        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
        }
    }

    console.log('Options:', options);

    try {
        const response = await fetch(url, options);
        console.log('Response status:', response.status);

        const contentType = response.headers.get('content-type');

        if (contentType && contentType.includes('application/json')) {
            const responseData = await response.json();
            console.log('Response JSON:', responseData);
            return {
                ok: response.ok,
                status: response.status,
                data: responseData
            };
        } else {
            const text = await response.text();
            console.error('Non-JSON response:', text);
            return {
                ok: false,
                status: response.status,
                data: { error: 'Server returned non-JSON response' }
            };
        }
    } catch (error) {
        console.error('Request failed:', error);
        return {
            ok: false,
            status: 0,
            data: { error: 'Network error' }
        };
    }
}

// Функция для сохранения токенов
function saveTokens(accessToken, refreshToken) {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
}

// Функция для проверки авторизации
function isAuthenticated() {
    return localStorage.getItem('access_token') !== null;
}

// Функция для обновления статуса авторизации в UI
function updateAuthStatus() {
    const accessToken = getAccessToken();
    const authStatus = document.getElementById('auth-status');
    const tokensDiv = document.getElementById('tokens');

    if (authStatus && tokensDiv) {
        if (accessToken) {
            authStatus.textContent = 'Авторизован';
            authStatus.className = 'success';
            tokensDiv.style.display = 'block';
            if (document.getElementById('access-token')) {
                document.getElementById('access-token').textContent = 'Access: ' + accessToken.substring(0, 50) + '...';
            }
            if (document.getElementById('refresh-token')) {
                document.getElementById('refresh-token').textContent = 'Refresh: ' + (getRefreshToken() || '').substring(0, 50) + '...';
            }
        } else {
            authStatus.textContent = 'Не авторизован';
            authStatus.className = 'error';
            tokensDiv.style.display = 'none';
        }
    }
}

// Функция для выхода
async function logout() {
    try {
        const response = await apiRequest('/users/api/logout/', 'POST', {}, true);

        if (response.ok) {
            console.log('Logout successful:', response.data.detail);
        } else {
            console.log('Logout API error, but clearing tokens locally');
        }
    } catch (error) {
        console.log('Logout request failed, clearing tokens locally');
    } finally {
        // Всегда очищаем токены локально
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/users/login/';
    }
}

// Функция для обновления навигации
function updateNavigation() {
    const isAuth = isAuthenticated();
    if (document.getElementById('auth-links') && document.getElementById('profile-links')) {
        document.getElementById('auth-links').style.display = isAuth ? 'none' : 'inline';
        document.getElementById('profile-links').style.display = isAuth ? 'inline' : 'none';
    }
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    updateAuthStatus();
    updateNavigation();
});