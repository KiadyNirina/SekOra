// Export par défaut pour le service principal
let baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default class GeocodingService {
    static PROXY_URL = `${baseUrl}/school/api/geocode/`;
    static REVERSE_PROXY_URL = `${baseUrl}/school/api/reverse-geocode/`;
    static USER_AGENT = 'VotreApplication/1.0';

    static async geocode(address, options = {}) {
        try {
            const params = new URLSearchParams({
                q: address,
                limit: options.limit || 1,
                format: 'json'
            });

            const response = await fetch(`${this.PROXY_URL}?${params}`, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }

            const data = await response.json();

            if (data && data.length > 0) {
                const result = data[0];
                return {
                    latitude: parseFloat(result.lat),
                    longitude: parseFloat(result.lon),
                    display_name: result.display_name,
                    address: result.address,
                    boundingbox: result.boundingbox,
                    class: result.class,
                    type: result.type,
                    importance: result.importance
                };
            }

            return null;
        } catch (error) {
            console.error('Erreur de géocodage:', error);
            throw new Error(`Impossible de géocoder l'adresse: ${error.message}`);
        }
    }

    static async reverseGeocode(lat, lng, options = {}) {
        try {
            const params = new URLSearchParams({
                lat: lat,
                lon: lng,
                format: 'json',
                zoom: options.zoom || 18
            });

            const response = await fetch(`${this.REVERSE_PROXY_URL}?${params}`, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }

            const data = await response.json();

            if (data && data.display_name) {
                return {
                    display_name: data.display_name,
                    address: data.address,
                    lat: parseFloat(data.lat),
                    lon: parseFloat(data.lon)
                };
            }

            return null;
        } catch (error) {
            console.error('Erreur de géocodage inverse:', error);
            throw new Error(`Impossible de géocoder la position: ${error.message}`);
        }
    }

    // La méthode search est maintenant correctement définie
    static async search(query, options = {}) {
        try {
            const params = new URLSearchParams({
                q: query,
                limit: options.limit || 5,
                format: 'json'
            });

            // Ajouter les filtres de pays si spécifiés
            if (options.countrycodes) {
                // Le proxy peut ajouter ce paramètre
            }

            const response = await fetch(`${this.PROXY_URL}?${params}`, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }

            const data = await response.json();

            if (!Array.isArray(data)) {
                return [];
            }

            return data.map(item => ({
                latitude: parseFloat(item.lat),
                longitude: parseFloat(item.lon),
                display_name: item.display_name,
                address: item.address,
                importance: item.importance
            }));
        } catch (error) {
            console.error('Erreur de recherche:', error);
            return [];
        }
    }

    static async validateAddress(address) {
        try {
            const results = await this.search(address, { limit: 3 });
            
            if (results.length > 0) {
                const firstResult = results[0];
                const confidence = firstResult.importance || 0;
                const valid = confidence > 0.5;

                return {
                    valid: valid,
                    suggestions: results.map(r => r.display_name),
                    bestMatch: firstResult
                };
            }

            return {
                valid: false,
                suggestions: [],
                bestMatch: null
            };
        } catch (error) {
            console.error('Erreur de validation:', error);
            return {
                valid: false,
                suggestions: [],
                bestMatch: null
            };
        }
    }
}

// Export des méthodes individuelles pour faciliter l'import
export const geocode = GeocodingService.geocode.bind(GeocodingService);
export const reverseGeocode = GeocodingService.reverseGeocode.bind(GeocodingService);
export const search = GeocodingService.search.bind(GeocodingService);
export const validateAddress = GeocodingService.validateAddress.bind(GeocodingService);

// Cache de géocodage
export class GeocodingCache {
    constructor() {
        this.cache = new Map();
        this.MAX_CACHE_SIZE = 100;
        this.CACHE_DURATION = 24 * 60 * 60 * 1000;
    }

    async geocode(address) {
        const key = address.toLowerCase().trim();
        
        if (this.cache.has(key)) {
            const cached = this.cache.get(key);
            if (Date.now() - cached.timestamp < this.CACHE_DURATION) {
                console.log('Cache hit:', address);
                return cached.data;
            } else {
                this.cache.delete(key);
            }
        }

        try {
            const result = await GeocodingService.geocode(address);
            
            if (result) {
                this.cache.set(key, {
                    data: result,
                    timestamp: Date.now()
                });

                if (this.cache.size > this.MAX_CACHE_SIZE) {
                    const firstKey = this.cache.keys().next().value;
                    this.cache.delete(firstKey);
                }
            }

            return result;
        } catch (error) {
            console.error('Erreur de géocodage:', error);
            throw error;
        }
    }

    async reverseGeocode(lat, lng) {
        const key = `${lat.toFixed(6)},${lng.toFixed(6)}`;
        
        if (this.cache.has(key)) {
            const cached = this.cache.get(key);
            if (Date.now() - cached.timestamp < this.CACHE_DURATION) {
                return cached.data;
            }
        }

        const result = await GeocodingService.reverseGeocode(lat, lng);
        
        if (result) {
            this.cache.set(key, {
                data: result,
                timestamp: Date.now()
            });
        }

        return result;
    }

    clearCache() {
        this.cache.clear();
        console.log('Cache vidé');
    }
}

// Créer une instance unique du cache
export const geocodingCache = new GeocodingCache();