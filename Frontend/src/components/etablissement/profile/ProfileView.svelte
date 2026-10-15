<script>
  import { onMount } from 'svelte';
  import Icon from '@iconify/svelte';
  import { authApi } from '../../../lib/api';
  
  let baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  export let etablissementId = null;
  $: isOwnProfile = !etablissementId; 

  export let onClose = null;
  
  let loading = true;
  let saving = false;
  let error = null;
  let success = false;
  
  // Données du profil
  let profile = {
    etablissement: {
      id: null,
      nom: '',
      type_etablissement: '',
      adresse: '',
      logo: null,
      description: '',
      site_web: '',
      user: {
        email: '',
        telephone: '',
        first_name: '',
        last_name: ''
      }
    },
    stats: {
      total_eleves: 0,
      total_professeurs: 0,
      total_classes: 0,
      total_matieres: 0
    },
    annees_scolaires: [],
    classes: [],
    professeurs: [],
    matieres: []
  };
  
  let isEditing = false;
  let formData = {};
  let profileImagePreview = null;
  let profileImageFile = null;
  
  const typeOptions = [
    { value: 'ecole', label: 'École primaire' },
    { value: 'college', label: 'Collège' },
    { value: 'lycee', label: 'Lycée' },
    { value: 'universite', label: 'Université' }
  ];

  function initMap() {
    const mapContainer = document.getElementById('map');
    if (!mapContainer) return;
    
    const lat = parseFloat(mapContainer.dataset.lat);
    const lon = parseFloat(mapContainer.dataset.lon);
    
    if (isNaN(lat) || isNaN(lon)) return;
    
    // Charger Leaflet dynamiquement
    const leafletCSS = document.createElement('link');
    leafletCSS.rel = 'stylesheet';
    leafletCSS.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    document.head.appendChild(leafletCSS);
    
    const leafletJS = document.createElement('script');
    leafletJS.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    leafletJS.onload = () => {
      const L = window.L;
      const map = L.map(mapContainer, {
        center: [lat, lon],
        zoom: 18,
        minZoom: 18,
        maxZoom: 18,
        zoomControl: false,
        scrollWheelZoom: false,
        doubleClickZoom: false,
        touchZoom: false,
        boxZoom: false,
        keyboard: false,
        dragging: false
      });
      
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(map);
      
      const marker = L.marker([lat, lon]).addTo(map);
      marker.bindPopup('<b>Établissement</b><br>Votre établissement');
      
      setTimeout(() => {
        map.invalidateSize();
      }, 100);
    };
    document.body.appendChild(leafletJS);
  }
  
  onMount(async () => {
    await loadProfile();
    setTimeout(initMap, 500);
  });
  
  async function loadProfile() {
    loading = true;
    error = null;
    
    try {

      if (etablissementId) {
        // --- Profil public ---
        const publicData = await authApi.getPublicEtablissement(etablissementId);
        profile = {
          etablissement: publicData,
          stats: publicData.stats || {},
          classes: publicData.classes || [],
          professeurs: publicData.professeurs || [],
          matieres: publicData.matieres || [],
          annees_scolaires: publicData.annees_scolaires || [],
          user: publicData.user || {}
        };

        if (publicData.user.profile_image) {
          profileImagePreview = `${publicData.user.profile_image}`;
        } else {
          profileImagePreview = null;
        }

        formData = { ...profile.etablissement, ...profile.user };
      
      } else {

        const userProfile = await authApi.getProfile();
        
        if (userProfile && userProfile.profile) {
          profile = {
            ...profile,
            etablissement: userProfile.profile,
            user: userProfile
          };
          
          // Charger les données statistiques
          await loadStats();
          await loadAnneeScolaire();
          await loadClasses();
          await loadProfesseurs();
          await loadMatieres();
          
          // Initialiser formData
          formData = {
            nom: profile.etablissement.nom || '',
            type_etablissement: profile.etablissement.type_etablissement || '',
            adresse: profile.etablissement.adresse || '',
            description: profile.etablissement.description || '',
            site_web: profile.etablissement.site_web || '',
            email: profile.user.email || '',
            telephone: profile.user.telephone || '',
            first_name: profile.user.first_name || '',
            last_name: profile.user.last_name || '',
            latitude: profile.etablissement.latitude || '',
            longitude: profile.etablissement.longitude || ''
          };
          
          // Charger le logo
          if (userProfile.profile.user.profile_image) {
            profileImagePreview = `${userProfile.profile.user.profile_image}`;
          } else {
            profileImagePreview = null;
          }
        } else {
          error = 'Aucune donnée d\'établissement trouvée';
        }
      }
    } catch (err) {
      console.error('Erreur chargement profil:', err);
      error = err.message || 'Erreur lors du chargement du profil';
    } finally {
      loading = false;
    }
  }
  
  async function loadStats() {
    try {
      const eleves = await authApi.getEleves({ etablissement: profile.etablissement.id });
      const professeurs = await authApi.getProfesseurs({ etablissement: profile.etablissement.id });
      const classes = await authApi.getClasses({ etablissement: profile.etablissement.id });
      const matieres = await authApi.getMatieres({ etablissement: profile.etablissement.id });
      
      profile.stats = {
        total_eleves: eleves.results ? eleves.results.length : eleves.length || 0,
        total_professeurs: professeurs.results ? professeurs.results.length : professeurs.length || 0,
        total_classes: classes.results ? classes.results.length : classes.length || 0,
        total_matieres: matieres.results ? matieres.results.length : matieres.length || 0
      };
    } catch (err) {
      console.error('Erreur chargement stats:', err);
    }
  }
  
  async function loadAnneeScolaire() {
    try {
      const annees = await authApi.getAnneesScolaires();
      profile.annees_scolaires = annees.results || annees || [];
    } catch (err) {
      console.error('Erreur chargement années scolaires:', err);
    }
  }
  
  async function loadClasses() {
    try {
      const classes = await authApi.getClasses({ etablissement: profile.etablissement.id });
      profile.classes = classes.results || classes || [];
    } catch (err) {
      console.error('Erreur chargement classes:', err);
    }
  }
  
  async function loadProfesseurs() {
    try {
      const professeurs = await authApi.getProfesseurs({ etablissement: profile.etablissement.id });
      profile.professeurs = professeurs.results || professeurs || [];
    } catch (err) {
      console.error('Erreur chargement professeurs:', err);
    }
  }
  
  async function loadMatieres() {
    try {
      const matieres = await authApi.getMatieres({ etablissement: profile.etablissement.id });
      profile.matieres = matieres.results || matieres || [];
    } catch (err) {
      console.error('Erreur chargement matières:', err);
    }
  }
  
  function toggleEdit() {
    if (isEditing) {
      // Annuler les modifications
      formData = {
        nom: profile.etablissement.nom || '',
        type_etablissement: profile.etablissement.type_etablissement || '',
        adresse: profile.etablissement.adresse || '',
        description: profile.etablissement.description || '',
        site_web: profile.etablissement.site_web || '',
        email: profile.user.email || '',
        telephone: profile.user.telephone || '',
        first_name: profile.user.first_name || '',
        last_name: profile.user.last_name || ''
      };
      logoPreview = profile.etablissement.logo || null;
      logoFile = null;
    }
    isEditing = !isEditing;
    error = null;
    success = false;
  }

  async function toggleCancel() {
    setTimeout(() => {
      initMap();
    }, 500);
    isEditing = false;
    error = null;
    success = false;
  }

  function handleFileChange(event) {
    const file = event.target.files[0];
    if (file) {
      profileImageFile = file;
      const reader = new FileReader();
      reader.onload = (e) => {
        profileImagePreview = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  }
  
  async function handleSave() {
    saving = true;
    error = null;
    success = false;

    try {
      const etabId = profile.etablissement.id;

      const formPayload = new FormData();
      
      formPayload.append('nom', formData.nom);
      formPayload.append('type_etablissement', formData.type_etablissement);
      formPayload.append('adresse', formData.adresse);
      formPayload.append('description', formData.description);
      formPayload.append('site_web', formData.site_web);
      if (formData.latitude) formPayload.append('latitude', formData.latitude);
      if (formData.longitude) formPayload.append('longitude', formData.longitude);

      formPayload.append('user.email', formData.email);
      formPayload.append('user.first_name', formData.nom);
      formPayload.append('user.last_name', '');
      formPayload.append('user.telephone', formData.telephone);

      if (profileImageFile) {
        formPayload.append('user.profile_image', profileImageFile);
      }

      await authApi.updateEtablissementProfile(etabId, formPayload);

      success = true;
      isEditing = false;
      profileImageFile = null;

      await loadProfile();
      setTimeout(() => {
        initMap();
      }, 500);
      
    } catch (err) {
      console.error('Erreur sauvegarde:', err);
      error = err.message || 'Erreur lors de la sauvegarde';
    } finally {
      saving = false;
    }
  }
  
  function getTypeLabel(type) {
    const option = typeOptions.find(t => t.value === type);
    return option ? option.label : type;
  }
  
  function formatDate(date) {
    if (!date) return 'N/A';
    return new Date(date).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  }
  
  function getInitials(firstName, lastName) {
    return `${firstName?.charAt(0) || ''}${lastName?.charAt(0) || ''}`.toUpperCase();
  }
</script>

<div class="mx-auto">
  <!-- En-tête -->
  <div class="mb-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Profil de l'établissement</h1>
        <p class="mt-1 text-sm text-gray-500">
          Gérez les informations publiques de votre établissement
        </p>
      </div>
      
      <div class="mt-4 sm:mt-0 flex space-x-3">
        {#if isOwnProfile && isEditing}
          <button
            on:click={toggleCancel}
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            disabled={saving}
          >
            Annuler
          </button>
          <button
            on:click={handleSave}
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            disabled={saving}
          >
            {#if saving}
              <Icon icon="heroicons:arrow-path" class="h-4 w-4 mr-2 animate-spin" />
              Sauvegarde...
            {:else}
              <Icon icon="heroicons:check" class="h-4 w-4 mr-2" />
              Enregistrer
            {/if}
          </button>
        {:else}
          <button
            on:click={toggleEdit}
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <Icon icon="heroicons:pencil-square" class="h-4 w-4 mr-2" />
            Modifier le profil
          </button>
        {/if}
      </div>
    </div>
  </div>
  
  <!-- Messages -->
  {#if success}
    <div class="mb-4 p-4 rounded-md bg-green-50 border border-green-200">
      <div class="flex">
        <Icon icon="heroicons:check-circle" class="h-5 w-5 text-green-400" />
        <div class="ml-3">
          <p class="text-sm font-medium text-green-800">Profil mis à jour avec succès</p>
        </div>
      </div>
    </div>
  {/if}
  
  {#if error}
    <div class="mb-4 p-4 rounded-md bg-red-50 border border-red-200">
      <div class="flex">
        <Icon icon="heroicons:x-circle" class="h-5 w-5 text-red-400" />
        <div class="ml-3">
          <p class="text-sm font-medium text-red-800">{error}</p>
        </div>
      </div>
    </div>
  {/if}
  
  <!-- Chargement -->
  {#if loading}
    <div class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
    </div>
  {:else}
  
  <!-- Section Logo et informations principales -->
  <div class="bg-white shadow rounded-lg overflow-hidden">
    <div class="p-6">
      <div class="flex flex-col md:flex-row items-start md:items-center space-y-4 md:space-y-0 md:space-x-6">
        <!-- Logo -->
        <div class="flex-shrink-0">
          <div class="relative">
            {#if profileImagePreview}
              <div class="h-32 w-32 rounded-lg overflow-hidden border-2 border-gray-200">
                <img src={profileImagePreview} alt="Logo de l'établissement" class="h-full w-full object-cover" />
              </div>
            {:else}
              <div class="h-32 w-32 rounded-lg bg-gradient-to-br from-green-100 to-green-200 flex items-center justify-center border-2 border-gray-200">
                <Icon icon="heroicons:user-circle" class="w-15 h-15 text-green-600" />
              </div>
            {/if}
            
            {#if isOwnProfile && isEditing}
              <label
                for="profile-image-upload"
                class="absolute bottom-0 right-0 p-1.5 bg-green-600 rounded-full cursor-pointer hover:bg-green-700 transition-colors shadow-lg"
              >
                <Icon icon="heroicons:camera" class="h-4 w-4 text-white" />
                <input
                  id="profile-image-upload"
                  type="file"
                  accept="image/*"
                  class="hidden"
                  on:change={handleFileChange}
                />
              </label>
            {/if}
          </div>
          
          {#if isOwnProfile && isEditing && profileImageFile}
            <p class="text-xs text-gray-500 mt-1">{profileImageFile.name}</p>
          {/if}
        </div>
        
        <!-- Informations principales -->
        <div class="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Nom de l'établissement
            </label>
            {#if isOwnProfile && isEditing}
              <input
                type="text"
                bind:value={formData.nom}
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 sm:text-sm"
                placeholder="Nom de l'établissement"
              />
            {:else}
              <p class="text-gray-900 font-medium">{profile.etablissement.nom || 'Non renseigné'}</p>
            {/if}
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Type d'établissement
            </label>
            {#if isOwnProfile && isEditing}
              <select
                bind:value={formData.type_etablissement}
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 sm:text-sm"
              >
                <option value="">Sélectionner un type</option>
                {#each typeOptions as option}
                  <option value={option.value}>{option.label}</option>
                {/each}
              </select>
            {:else}
              <p class="text-gray-900">{getTypeLabel(profile.etablissement.type_etablissement) || 'Non renseigné'}</p>
            {/if}
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
    
    <!-- Colonne de gauche : Présentation & Contact -->
    <div class="bg-white shadow rounded-lg overflow-hidden">
      <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
        <h2 class="text-lg font-medium text-gray-900">Présentation & Contact</h2>
      </div>
      
      <div class="p-6 space-y-6">
        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
          {#if isOwnProfile && isEditing}
            <textarea
              bind:value={formData.description}
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 sm:text-sm"
              placeholder="Description de l'établissement"
            />
          {:else}
            <p class="text-gray-900">{profile.etablissement.description || 'Aucune description renseignée'}</p>
          {/if}
        </div>
        
        <!-- Site web & Téléphone -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Site web</label>
            {#if isOwnProfile && isEditing}
              <input
                type="url"
                bind:value={formData.site_web}
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 sm:text-sm"
                placeholder="https://www.etablissement.fr"
              />
            {:else}
              {#if profile.etablissement.site_web}
                <a href={profile.etablissement.site_web} target="_blank" rel="noopener noreferrer" class="text-green-600 hover:text-green-700 hover:underline">
                  {profile.etablissement.site_web}
                </a>
              {:else}
                <p class="text-gray-500">Non renseigné</p>
              {/if}
            {/if}
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Téléphone</label>
            {#if isOwnProfile && isEditing}
              <input
                type="tel"
                bind:value={formData.telephone}
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 sm:text-sm"
                placeholder="01 23 45 67 89"
              />
            {:else}
              <p class="text-gray-900">{profile.user.telephone || 'Non renseigné'}</p>
            {/if}
          </div>
        </div>
        
        <!-- Adresse & Email -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Adresse</label>
            {#if isOwnProfile && isEditing}
              <textarea
                bind:value={formData.adresse}
                rows="2"
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 sm:text-sm"
                placeholder="Adresse complète"
              />
            {:else}
              <p class="text-gray-900">{profile.etablissement.adresse || 'Non renseignée'}</p>
            {/if}
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            {#if isOwnProfile && isEditing}
              <input
                type="email"
                bind:value={formData.email}
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 sm:text-sm"
                placeholder="email@etablissement.fr"
              />
            {:else}
              <p class="text-gray-900">{profile.user.email || 'Non renseigné'}</p>
            {/if}
          </div>
        </div>
      </div>
    </div>
  
    <!-- Colonne de droite : Localisation -->
    <div class="bg-white shadow rounded-lg overflow-hidden">
      <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
        <h2 class="text-lg font-medium text-gray-900">Localisation</h2>
      </div>
      
      <div class="p-6 space-y-4">
        {#if isOwnProfile && isEditing}
          <div class="grid grid-cols-1 gap-3">
            <div>
              <label class="block text-xs text-gray-500 mb-1">Latitude</label>
              <input
                type="number"
                step="0.000001"
                bind:value={formData.latitude}
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 sm:text-sm"
                placeholder="48.856614"
              />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Longitude</label>
              <input
                type="number"
                step="0.000001"
                bind:value={formData.longitude}
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 sm:text-sm"
                placeholder="2.352222"
              />
            </div>
            <p class="text-xs text-gray-500">
              <Icon icon="heroicons:information-circle" class="h-4 w-4 inline mr-1" />
              Coordonnées GPS de l'établissement
            </p>
          </div>
        {:else}
          {#if profile.etablissement.latitude && profile.etablissement.longitude}
            <div class="flex items-center space-x-2 text-sm text-gray-600">
              <Icon icon="heroicons:map-pin" class="h-5 w-5 text-green-600" />
              <span>
                <span class="font-mono">{Number(profile.etablissement.latitude).toFixed(6)}</span>, 
                <span class="font-mono">{Number(profile.etablissement.longitude).toFixed(6)}</span>
              </span>
            </div>
            
            <!-- Carte Leaflet -->
            <div class="relative w-full h-64 md:h-72 rounded-lg overflow-hidden border border-gray-200">
              <div 
                id="map" 
                class="w-full h-full"
                data-lat={profile.etablissement.latitude}
                data-lon={profile.etablissement.longitude}
              ></div>
              
              <div class="absolute bottom-2 right-2 bg-white rounded-md shadow-md px-2 py-1 text-xs text-gray-600 z-10">
                <a 
                  href="https://www.openstreetmap.org/?mlat={Number(profile.etablissement.latitude)}&mlon={Number(profile.etablissement.longitude)}&zoom=16"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="hover:text-green-600 flex items-center space-x-1"
                >
                  <Icon icon="heroicons:arrow-top-right-on-square" class="h-3 w-3" />
                  <span>Agrandir</span>
                </a>
              </div>
            </div>
            
            <!-- Liens cartes externes -->
            <div class="flex flex-wrap gap-3 text-sm">
              <a 
                href="https://www.google.com/maps?q={Number(profile.etablissement.latitude)},{Number(profile.etablissement.longitude)}"
                target="_blank"
                rel="noopener noreferrer"
                class="text-green-600 hover:text-green-700 hover:underline flex items-center space-x-1"
              >
                <Icon icon="heroicons:map-pin" class="h-4 w-4" />
                <span>Google Maps</span>
              </a>
              <a 
                href="https://www.openstreetmap.org/?mlat={Number(profile.etablissement.latitude)}&mlon={Number(profile.etablissement.longitude)}&zoom=16"
                target="_blank"
                rel="noopener noreferrer"
                class="text-green-600 hover:text-green-700 hover:underline flex items-center space-x-1"
              >
                <Icon icon="heroicons:globe-alt" class="h-4 w-4" />
                <span>OpenStreetMap</span>
              </a>
            </div>
          {:else}
            <div class="flex items-center space-x-2 text-sm text-gray-500 py-8">
              <Icon icon="heroicons:map-pin" class="h-5 w-5 text-gray-400" />
              <span>Aucune coordonnée GPS renseignée</span>
            </div>
            {#if isOwnProfile && !isEditing}
              <p class="text-xs text-gray-400">
                Passez en mode édition pour ajouter la localisation
              </p>
            {/if}
          {/if}
        {/if}
      </div>
    </div>
  </div>
  
  <!-- Statistiques -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-6">
    <div class="bg-white shadow rounded-lg p-6">
      <div class="flex items-center">
        <div class="p-3 rounded-full bg-blue-100">
          <Icon icon="heroicons:user-group" class="h-6 w-6 text-blue-600" />
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-500">Élèves</p>
          <p class="text-2xl font-semibold text-gray-900">{profile.stats.total_eleves}</p>
        </div>
      </div>
    </div>
    
    <div class="bg-white shadow rounded-lg p-6">
      <div class="flex items-center">
        <div class="p-3 rounded-full bg-green-100">
          <Icon icon="heroicons:academic-cap" class="h-6 w-6 text-green-600" />
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-500">Professeurs</p>
          <p class="text-2xl font-semibold text-gray-900">{profile.stats.total_professeurs}</p>
        </div>
      </div>
    </div>
    
    <div class="bg-white shadow rounded-lg p-6">
      <div class="flex items-center">
        <div class="p-3 rounded-full bg-purple-100">
          <Icon icon="heroicons:book-open" class="h-6 w-6 text-purple-600" />
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-500">Classes</p>
          <p class="text-2xl font-semibold text-gray-900">{profile.stats.total_classes}</p>
        </div>
      </div>
    </div>
    
    <div class="bg-white shadow rounded-lg p-6">
      <div class="flex items-center">
        <div class="p-3 rounded-full bg-yellow-100">
          <Icon icon="heroicons:bookmark" class="h-6 w-6 text-yellow-600" />
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-500">Matières</p>
          <p class="text-2xl font-semibold text-gray-900">{profile.stats.total_matieres}</p>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Années scolaires -->
  {#if profile.annees_scolaires.length > 0}
    <div class="bg-white shadow rounded-lg overflow-hidden mt-6">
      <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
        <h2 class="text-lg font-medium text-gray-900">Années scolaires</h2>
      </div>
      
      <div class="p-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {#each profile.annees_scolaires as annee}
            <div class="p-4 border border-gray-200 rounded-lg {annee.est_active ? 'bg-green-50 border-green-200' : ''}">
              <div class="flex items-center justify-between">
                <span class="font-medium text-gray-900">{annee.nom}</span>
                {#if annee.est_active}
                  <span class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                    Active
                  </span>
                {/if}
              </div>
              <p class="text-sm text-gray-500 mt-1">
                {formatDate(annee.date_debut)} - {formatDate(annee.date_fin)}
              </p>
            </div>
          {/each}
        </div>
      </div>
    </div>
  {/if}
  
  <!-- Aperçu rapide -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
    <!-- Dernières classes -->
    {#if profile.classes.length > 0}
      <div class="bg-white shadow rounded-lg overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-sm font-medium text-gray-900">Classes récentes</h3>
        </div>
        <div class="p-4">
          <ul class="divide-y divide-gray-200">
            {#each profile.classes.slice(0, 5) as classe}
              <li class="py-2">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-900">{classe.nom}</span>
                  <span class="text-xs text-gray-500">{classe.niveau || ''}</span>
                </div>
              </li>
            {/each}
          </ul>
        </div>
      </div>
    {/if}
    
    <!-- Dernières matières -->
    {#if profile.matieres.length > 0}
      <div class="bg-white shadow rounded-lg overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-sm font-medium text-gray-900">Matières enseignées</h3>
        </div>
        <div class="p-4">
          <ul class="divide-y divide-gray-200">
            {#each profile.matieres.slice(0, 5) as matiere}
              <li class="py-2">
                <span class="text-sm text-gray-900">{matiere.nom}</span>
              </li>
            {/each}
          </ul>
        </div>
      </div>
    {/if}
  </div>
  
  {/if}
</div>

<style>
  :global(.leaflet-control-attribution) {
    display: none !important;
  }
</style>