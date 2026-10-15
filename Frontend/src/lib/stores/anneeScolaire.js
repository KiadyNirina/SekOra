import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { authApi } from '$lib/api.js';

export const anneesScolaires = writable([]);
export const anneeActive = derived(anneesScolaires, $annees =>
    $annees.find(a => a.est_active) || null
);

export async function loadAnneesScolaires() {
    try {
        const data = await authApi.getAnneesScolaires();
        const list = Array.isArray(data) ? data : (data.results ?? []);
        anneesScolaires.set(list);
        return list;
    } catch {
        anneesScolaires.set([]);
        return [];
    }
}