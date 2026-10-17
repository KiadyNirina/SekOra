import { token, refreshToken, userProfile, userRole } from "../stores/auth";
import { get } from "svelte/store";

// Synchroniser les modifications des stores avec localStorage

let baseUrl = import.meta.env.VITE_API_BASE_URL;
const API_URL = baseUrl+'/school/schoolLogin';

export async function login(email, password) {
    try{
        const respose = await fetch(`${API_URL}/token/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify({ email, password })
        });

        if (!respose.ok) {
            throw new Error('Login failed');
        }

        const data = await respose.json();
        token.set(data.access);
        refreshToken.set(data.refresh);

        return true;
    } catch (error) {
        console.error('Login error', error);
        return false
    }
}

export async function logout() {
    token.set('');
    refreshToken.set('');
    userProfile.set(null);
    localStorage.removeItem('jwtToken');
    localStorage.removeItem('refreshToken');
}

export async function refreshAccessToken() {
    try {
        const refresh_token = get(refreshToken);
        const response = await fetch(`${API_URL}/refresh/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ refresh: refresh_token })
        });

        if(!response.ok) {
            throw new Error('Refresh token failed');
        }

        const data = await response.json();
        token.set(data.access);
        localStorage.setItem('jwtToken', data.access);
    } catch (error) {
        console.error('Refresh token error:', error);
        logout();
    }
}

export async function getUserProfile() {
    const userToken = get(token);
    try {
        const response = await fetch('http://localhost:8000/school/user_profile/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${userToken}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if(!response.ok) {
            throw new Error('Failed to fetch user profile');
        }

        return data;
    } catch (error) {
        console.error('Error fetching user profile:', error);
        return null;
    }
}

export async function getUserStudent() {
    const userToken = get(token);
    try {
        const response = await fetch('http://localhost:8000/school/user_student/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${userToken}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if(!response.ok) {
            throw new Error('Failed to fetch user profile');
        }

        return data;
    } catch (error) {
        console.error('Error fetching user profile:', error);
        return null;
    }
}