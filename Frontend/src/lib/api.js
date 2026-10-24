// src/lib/api.js
import { browser } from '$app/environment';

const API_BASE_URL = `${import.meta.env.VITE_API_BASE_URL}/school`;

function formatDjangoError(errorData) {
    if (!errorData) return 'Erreur inconnue';
    
    if (typeof errorData === 'string') {
        return errorData;
    }
    
    if (typeof errorData === 'object') {
        const messages = [];
        
        for (const [key, value] of Object.entries(errorData)) {
            if (typeof value === 'string') {
                messages.push(`${key}: ${value}`);
            }
            else if (Array.isArray(value)) {
                if (value.length > 0 && typeof value[0] === 'object') {
                    const nestedErrors = value.map(item => formatDjangoError(item)).join('; ');
                    messages.push(`${key}: ${nestedErrors}`);
                } else {
                    messages.push(`${key}: ${value.join(', ')}`);
                }
            }
            else if (typeof value === 'object' && value !== null) {
                messages.push(formatDjangoError(value));
            }
        }
        
        return messages.length > 0 ? messages.join('; ') : 'Erreur de validation';
    }
    
    return String(errorData);
}

async function fetchWithAuth(endpoint, options = {}) {
    const accessToken = browser ? localStorage.getItem('access_token') : null;
    const refreshToken = browser ? localStorage.getItem('refresh_token') : null;
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
    }

    const config = {
        ...options,
        headers,
        credentials: 'include',
    };

    let response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    
    if (response.status === 401 && refreshToken && browser) {
        try {
            const newTokens = await refreshAuthToken(refreshToken);
            headers['Authorization'] = `Bearer ${newTokens.access}`;
            response = await fetch(`${API_BASE_URL}${endpoint}`, { ...config, headers });
        } catch (refreshError) {
            authStore.clearTokens();
            throw new Error('Session expirée, veuillez vous reconnecter');
        }
    }
    
    if (!response.ok) {
        let errorData = {};
        let errorMessage = '';
        
        try {
            errorData = await response.json();
        } catch (e) {
            const text = await response.text().catch(() => '');
            errorMessage = text || `Erreur ${response.status}: ${response.statusText}`;
        }
        
        if (errorData) {
            if (errorData.detail) {
                errorMessage = errorData.detail;
            } 
            else if (typeof errorData === 'object') {
                errorMessage = formatDjangoError(errorData);
            }
            else {
                errorMessage = String(errorData);
            }
        }
        
        const error = new Error(errorMessage);
        error.response = {
            status: response.status,
            data: errorData,
            statusText: response.statusText
        };
        
        console.error('API Error:', {
            endpoint,
            status: response.status,
            data: errorData,
            message: errorMessage
        });
        
        throw error;
    }
    
    return response;
}

async function fetchWithAuthFormData(endpoint, method, formData) {
  const accessToken = browser ? localStorage.getItem('access_token') : null;
  const refreshToken = browser ? localStorage.getItem('refresh_token') : null;

  const headers = {};
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }

  const config = {
    method,
    headers,
    body: formData,
    credentials: 'include',
  };

  let response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  // Gestion du rafraîchissement de token
  if (response.status === 401 && refreshToken && browser) {
    try {
      const newTokens = await refreshAuthToken(refreshToken);
      headers['Authorization'] = `Bearer ${newTokens.access}`;
      config.headers = headers;
      response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    } catch (refreshError) {
      authStore.clearTokens();
      throw new Error('Session expirée, veuillez vous reconnecter');
    }
  }

  if (!response.ok) {
    let errorMessage = '';
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || formatDjangoError(errorData);
    } catch (e) {
      errorMessage = `Erreur ${response.status}: ${response.statusText}`;
    }
    const error = new Error(errorMessage);
    error.response = { status: response.status, data: {} };
    throw error;
  }

  return response;
}

async function refreshAuthToken(refreshToken) {
    const response = await fetch(`${API_BASE_URL}/token/refresh/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: refreshToken })
    });

    if (!response.ok) {
        throw new Error('Échec du rafraîchissement du token');
    }

    const tokens = await response.json();
    authStore.setTokens(tokens);
    return tokens;
}

async function registerPublic(endpoint, data) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        let errorData = {};
        let errorMessage = '';
        
        try {
            errorData = await response.json();
        } catch (e) {
            errorMessage = await response.text().catch(() => '');
        }
        
        if (errorData) {
            if (errorData.detail) {
                errorMessage = errorData.detail;
            } else if (typeof errorData === 'object') {
                errorMessage = formatDjangoError(errorData);
            } else {
                errorMessage = String(errorData);
            }
        }
        
        const error = new Error(errorMessage || "Erreur lors de l'inscription");
        error.response = { status: response.status, data: errorData };
        throw error;
    }

    const result = await response.json();

    if (result.tokens?.access && result.tokens?.refresh) {
        authStore.setTokens({
            access: result.tokens.access,
            refresh: result.tokens.refresh,
        });
    }

    return result;
}

async function login(username, password) {
    const response = await fetch(`${API_BASE_URL}/token/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
    });

    let data = {};

    try {
        data = await response.json();
    } catch {
        throw new Error(`Erreur ${response.status}: ${response.statusText}`);
    }

    if (!response.ok) {
        const error = new Error(
            data.detail || formatDjangoError(data) || 'Erreur de connexion'
        );

        error.response = {
            status: response.status,
            data,
            statusText: response.statusText,
        };

        throw error;
    }

    return data;
}

export const authApi = {
    // Authentification
    login: login,

    refreshToken: () => {
        const refreshToken = browser ? localStorage.getItem('refresh_token') : null;
        if (!refreshToken) throw new Error('No refresh token');
        return refreshAuthToken(refreshToken);
    },

    // Inscriptions (publiques)
    registerEtablissement: (data) => registerPublic('/register/etablissement/', data),
    registerProfesseur: (data) => registerPublic('/register/professeur/', data),
    registerEleve: (data) => registerPublic('/register/eleve/', data),
    registerParent: (data) => registerPublic('/register/parent/', data),

    // Gestion des établissements avec géolocalisation
    getEtablissements: (filters = {}) => {
        const query = new URLSearchParams();
        
        // Filtres existants
        if (filters.type && filters.type !== 'all') {
            query.append('type', filters.type);
        }
        
        if (filters.search && filters.search.trim()) {
            query.append('search', filters.search.trim());
        }
        
        // Filtres de géolocalisation
        if (filters.lat && filters.lng) {
            query.append('lat', filters.lat);
            query.append('lng', filters.lng);
            query.append('radius', filters.radius || 50);
        }
        
        if (filters.only_with_coords) {
            query.append('with_coords', 'true');
        }
        
        const queryString = query.toString();
        const url = `/api/etablissements/${queryString ? '?' + queryString : ''}`;
        
        return fetchWithAuth(url).then(response => response.json());
    },

    getPublicEtablissement: (id) => fetchWithAuth(`/api/etablissements/${id}/`).then(response => response.json()),

    // Créer un établissement (avec géocodage automatique)
    createEtablissement: (data) => fetchWithAuth('/api/etablissements/', {
        method: 'GET',
        body: JSON.stringify(data),
    }).then(response => response.json()),

    // Mettre à jour un établissement
    updateEtablissement: (id, data) => fetchWithAuth(`/api/etablissements/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(data),
    }).then(response => response.json()),

    updateEtablissementProfile: (id, formData) => {
        return fetchWithAuthFormData(`/api/etablissements/${id}/`, 'PATCH', formData)
        .then(response => response.json());
    },

    // Supprimer un établissement
    deleteEtablissement: (id) => fetchWithAuth(`/api/etablissements/${id}/`, {
        method: 'DELETE',
    }).then(() => ({ message: 'Établissement supprimé' })),

    // Recherche d'établissements à proximité
    getNearbyEtablissements: (lat, lng, radius = 10) => {
        const query = new URLSearchParams({
            lat: lat,
            lng: lng,
            radius: radius,
            with_coords: true
        });
        
        return fetchWithAuth(`/api/etablissements/nearby/?${query}`)
            .then(response => response.json());
    },

    // Mettre à jour les coordonnées d'un établissement spécifique
    updateEtablissementCoordinates: (id, latitude = null, longitude = null) => {
        const data = {};
        if (latitude !== null) data.latitude = latitude;
        if (longitude !== null) data.longitude = longitude;
        
        return fetchWithAuth(`/api/etablissements/${id}/update_coordinates/`, {
            method: 'POST',
            body: JSON.stringify(data),
        }).then(response => response.json());
    },

    // Géocoder en lot tous les établissements sans coordonnées (admin seulement)
    geocodeAllEtablissements: () => fetchWithAuth('/api/etablissements/geocode/', {
        method: 'POST',
    }).then(response => response.json()),

    // Récupérer les types d'établissements pour les filtres
    getEtablissementTypes: () => {
        // Vous pouvez ajouter un endpoint dédié ou utiliser les données du modèle
        return Promise.resolve({
            types: [
                { value: 'ecole', label: 'École primaire' },
                { value: 'college', label: 'Collège' },
                { value: 'lycee', label: 'Lycée' },
                { value: 'universite', label: 'Université' },
            ]
        });
    },

    getAnneesScolaires: () => fetchWithAuth('/api/annees-scolaires/').then(response => response.json()),
    
    createAnneeScolaire: (data) => fetchWithAuth('/api/annees-scolaires/', {
        method: 'POST',
        body: JSON.stringify(data),
    }).then(response => response.json()),

    updateAnneeScolaire: (id, data) => fetchWithAuth(`/api/annees-scolaires/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(data),
    }).then(response => response.json()),

    deleteAnneeScolaire: (id) => fetchWithAuth(`/api/annees-scolaires/${id}/`, {
        method: 'DELETE',
    }).then(() => ({ message: 'Année scolaire supprimée' })),

    activateAnneeScolaire: (id) => fetchWithAuth(`/api/annees-scolaires/${id}/activate/`, {
        method: 'POST',
    }).then(response => response.json()),

    // Gestion des classes
    getClasses: (filters = {}) => {
        const query = new URLSearchParams(filters).toString();
        return fetchWithAuth(`/api/classes/?${query}`).then(response => response.json());
    },

    createClasse: (data) => fetchWithAuth('/api/classes/', {
        method: 'POST',
        body: JSON.stringify(data),
    }).then(response => response.json()),

    updateClasse: (id, data) => fetchWithAuth(`/api/classes/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(data),
    }).then(response => response.json()),

    deleteClasse: (id) => fetchWithAuth(`/api/classes/${id}/`, {
        method: 'DELETE',
    }).then(() => ({ message: 'Classe supprimée' })),

    getMatieres: (filters = {}) => {
        const query = new URLSearchParams();
        if (filters.etablissement) query.append('etablissement', filters.etablissement);
        if (filters.annee_scolaire) query.append('annee_scolaire', filters.annee_scolaire);
        if (filters.search) query.append('search', filters.search);
        return fetchWithAuth(`/api/matieres/?${query.toString()}`).then(r => r.json());
    },

    createMatiere: (data) => fetchWithAuth('/api/matieres/', {
        method: 'POST',
        body: JSON.stringify(data),
    }).then(response => response.json()),

    updateMatiere: (id, data) => fetchWithAuth(`/api/matieres/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(data),
    }).then(response => response.json()),

    deleteMatiere: (id) => fetchWithAuth(`/api/matieres/${id}/`, {
        method: 'DELETE',
    }).then(() => ({ message: 'Matière supprimée' })),

    getSalles: (filters = {}) => {
        const query = new URLSearchParams(filters).toString();
        return fetchWithAuth(`/api/salles/?${query}`).then(response => response.json());
    },

    createSalle: (data) => fetchWithAuth('/api/salles/', {
        method: 'POST',
        body: JSON.stringify(data),
    }).then(response => response.json()),

    updateSalle: (id, data) => fetchWithAuth(`/api/salles/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(data),
    }).then(response => response.json()),

    deleteSalle: (id) => fetchWithAuth(`/api/salles/${id}/`, {
        method: 'DELETE',
    }).then(() => ({ message: 'Salle supprimée' })),

    // Gestion des cours
    getCours: (filters = {}) => {
        const query = new URLSearchParams(filters).toString();
        return fetchWithAuth(`/api/cours/?${query}`).then(response => response.json());
    },

    createCours: (data) => fetchWithAuth('/api/cours/', {
        method: 'POST',
        body: JSON.stringify(data),
    }).then(response => response.json()),

    updateCours: (id, data) => fetchWithAuth(`/api/cours/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(data),
    }).then(response => response.json()),

    deleteCours: (id) => fetchWithAuth(`/api/cours/${id}/`, {
        method: 'DELETE',
    }).then(() => ({ message: 'Cours supprimé' })),

    // Récupérer les options pour les filtres (classes, professeurs, matieres, salles)
    getCoursFilterOptions: () => fetchWithAuth('/api/cours/filter_options/').then(response => response.json()),

    // Profil utilisateur
    getProfile: () => fetchWithAuth('/profile/').then(response => response.json()),

    // Gestion des élèves
    getEleves: (filters = {}) => {
        const query = new URLSearchParams(filters).toString();
        return fetchWithAuth(`/api/eleves/?${query}`).then(response => response.json());
    },

    getFilterOptions: () => fetchWithAuth('/api/eleves/filter_options/').then(response => response.json()),

    createEleve: (data) => fetchWithAuth('/api/eleves/', {
        method: 'POST',
        body: JSON.stringify(data),
    }).then(response => response.json()),

    updateEleve: (id, data) => fetchWithAuth(`/api/eleves/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(data),
    }).then(response => response.json()),

    deleteEleve: (id) => fetchWithAuth(`/api/eleves/${id}/`, {
        method: 'DELETE',
    }).then(() => ({ message: 'Élève supprimé' })),

    bulkAction: (action, ids) => {
        if (action === 'export') {
            return fetchWithAuth('/api/eleves/bulk/', {
                method: 'POST',
                body: JSON.stringify({ action, ids }),
            });
        }
        return fetchWithAuth('/api/eleves/bulk/', {
            method: 'POST',
            body: JSON.stringify({ action, ids }),
        }).then(response => response.json());
    },

    
    getProfesseurFilterOptions: () => fetchWithAuth('/api/professeurs/filter_options/').then(response => response.json()),

    getProfesseurs: (filters = {}) => {
        const query = new URLSearchParams(filters).toString();

        return fetchWithAuth(`/api/professeurs/?${query}`)
            .then(response => response.json());
    },

    createProfesseur: (data) => fetchWithAuth('/api/professeurs/', {
        method: 'POST',
        body: JSON.stringify(data),
    }).then(response => response.json()),

    updateProfesseur: (id, data) => fetchWithAuth(`/api/professeurs/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(data),
    }).then(response => response.json()),

    deleteProfesseur: (id) => fetchWithAuth(`/api/professeurs/${id}/`, {
        method: 'DELETE',
    }).then(() => ({ message: 'Professeur supprimé' })),

    
    getPeriodes: (filters = {}) => {
        const query = new URLSearchParams(filters).toString();
        return fetchWithAuth(`/api/periodes/?${query}`).then(res => res.json());
    },

    getEvaluations: (filters = {}) => {
        const query = new URLSearchParams(filters).toString();
        return fetchWithAuth(`/api/evaluations/?${query}`).then(res => res.json());
    },

    getEvaluationDetail: (id) => fetchWithAuth(`/api/evaluations/${id}/`).then(res => res.json()),

    createEvaluation: (data) => fetchWithAuth('/api/evaluations/', {
        method: 'POST',
        body: JSON.stringify(data),
    }).then(res => res.json()),

    updateEvaluation: (id, data) => fetchWithAuth(`/api/evaluations/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
    }).then(res => res.json()),

    deleteEvaluation: (id) => fetchWithAuth(`/api/evaluations/${id}/`, {
        method: 'DELETE',
    }).then(() => ({ message: 'Évaluation supprimée' })),

    manageNotes: (evaluationId, notes) => fetchWithAuth(`/api/evaluations/${evaluationId}/manage_notes/`, {
        method: 'POST',
        body: JSON.stringify({ notes }),
    }).then(res => res.json()),

    publishEvaluation: (id) => fetchWithAuth(`/api/evaluations/${id}/publier/`, {
        method: 'POST',
    }).then(res => res.json()),

    unpublishEvaluation: (id) => fetchWithAuth(`/api/evaluations/${id}/brouillon/`, {
        method: 'POST',
    }).then(res => res.json()),
};

export const authStore = {
    subscribe(callback) {
        if (!browser) {
            callback({
                accessToken: null,
                refreshToken: null,
                isAuthenticated: false,
            });
            return () => {};
        }

        const handler = () => {
            callback({
                accessToken: localStorage.getItem('access_token'),
                refreshToken: localStorage.getItem('refresh_token'),
                isAuthenticated: !!localStorage.getItem('access_token'),
            });
        };

        window.addEventListener('storage', handler);
        handler();
        return () => window.removeEventListener('storage', handler);
    },
    
    setTokens({ access, refresh }) {
        if (!browser) return;
        if (access) localStorage.setItem('access_token', access);
        if (refresh) localStorage.setItem('refresh_token', refresh);
        window.dispatchEvent(new Event('storage'));
    },
    
    clearTokens() {
        if (!browser) return; 
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.dispatchEvent(new Event('storage'));
    },
    
    getAccessToken() {
        return browser ? localStorage.getItem('access_token') : null;
    },
    
    getRefreshToken() {
        return browser ? localStorage.getItem('refresh_token') : null;
    }
};