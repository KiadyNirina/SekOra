<!-- src/components/etablissement/map/EstablishmentList.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';
  import Icon from '@iconify/svelte';
  import { formatDistance, calculateDistance } from './mapUtils';

  export let establishments = [];
  export let userLocation = null;
  export let searchQuery = '';
  export let filterType = 'all';
  export let loading = false;

  export let loadingGoogle = false;

  export let selectedId = null;
  export let sourceFilter = 'all';

  export let distanceFilter = 0;

  function handleSourceFilter(e) {
    dispatch('filterSource', e.target.value);
  }

  function handleDistanceFilter(e) {
    dispatch('filterDistance', e.target.value);
  }

  const dispatch = createEventDispatcher();
  const typeLabels = {
    ecole: 'École primaire',
    college: 'Collège',
    lycee: 'Lycée',
    universite: 'Université'
  };

  function handleSearch(e) {
    dispatch('search', e.target.value);
  }

  function handleFilter(e) {
    dispatch('filter', e.target.value);
  }

  function handleClear() {
    dispatch('clear');
  }

  function handleSelect(establishment) {
    dispatch('select', establishment.id);
  }

  function getEstablishmentDistance(establishment) {
    if (!userLocation) return null;
    if (!establishment.lat && !establishment.latitude) return null;
    const lat = establishment.lat || parseFloat(establishment.latitude);
    const lng = establishment.lng || parseFloat(establishment.longitude);
    if (!lat || !lng) return null;
    return calculateDistance(userLocation.lat, userLocation.lng, lat, lng);
  }
</script>

<div class="w-full h-full flex flex-col bg-white shadow-2xl">
  <!-- En-tête -->
  <div class="p-4 sm:p-5 border-b border-gray-100 flex items-center justify-between bg-white shrink-0">
    <div class="flex items-center space-x-3">
      <button
        on:click={() => dispatch('back')}
        class="text-gray-500 hover:text-[#20784d] transition-colors p-2 rounded-full hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-[#20784d]/50"
      >
        <Icon icon="heroicons:arrow-left" class="h-5 w-5" />
      </button>
      <h1 class="text-lg font-medium text-gray-900 leading-tight">Recherche</h1>
    </div>

    {#if userLocation}
      <button
        on:click={() => dispatch('goToUserLocation')}
        class="flex items-center gap-1.5 text-xs font-medium bg-green-50 text-[#20784d] px-3 py-1.5 rounded-full hover:bg-[#20784d] hover:text-white transition-all border border-green-100"
      >
        <Icon icon="heroicons:map-pin" class="h-4 w-4" />
        Ma position
      </button>
    {/if}
  </div>

  <!-- Filtres -->
  <div class="p-4 sm:px-5 bg-gray-50/50 border-b border-gray-100 shrink-0 space-y-3">
    <div class="relative">
      <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
        <Icon icon="heroicons:magnifying-glass" class="h-4 w-4 text-gray-400" />
      </div>
      <input
        type="text"
        placeholder="Nom, adresse, type..."
        value={searchQuery}
        on:input={handleSearch}
        class="block w-full pl-10 pr-4 py-2.5 bg-white border border-gray-200 rounded-full text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#20784d]/50 focus:border-[#20784d] transition-all"
      />
    </div>

    <div class="flex gap-2">
      <div class="relative flex-1">
        <select
          value={filterType}
          on:change={handleFilter}
          class="block w-full pl-3 pr-8 py-2 bg-white border border-gray-200 rounded-full text-sm text-gray-700 appearance-none focus:outline-none focus:ring-2 focus:ring-[#20784d]/50 focus:border-[#20784d] transition-all"
        >
          <option value="all">Tous les types</option>
          <option value="ecole">École primaire</option>
          <option value="college">Collège</option>
          <option value="lycee">Lycée</option>
          <option value="universite">Université</option>
        </select>
        <div class="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
          <Icon icon="heroicons:chevron-down" class="h-4 w-4 text-gray-400" />
        </div>
      </div>

      <button
        on:click={handleClear}
        class="px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-full hover:bg-gray-50 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-200 transition-all flex items-center gap-1"
        title="Réinitialiser"
      >
        <Icon icon="heroicons:arrow-path" class="h-4 w-4" />
      </button>
    </div>

    <!-- Filtre source -->
    <div class="flex items-center gap-1 p-1 bg-white border border-gray-200 rounded-full">
      <button
        on:click={() => dispatch('filterSource', 'all')}
        class="flex-1 text-xs font-medium px-3 py-1.5 rounded-full transition-all
              {sourceFilter === 'all' ? 'bg-[#20784d] text-white shadow-sm' : 'text-gray-600 hover:bg-gray-50'}"
      >
        Tout
      </button>
      <button
        on:click={() => dispatch('filterSource', 'registered')}
        class="flex-1 text-xs font-medium px-3 py-1.5 rounded-full transition-all flex items-center justify-center gap-1
              {sourceFilter === 'registered' ? 'bg-[#20784d] text-white shadow-sm' : 'text-gray-600 hover:bg-gray-50'}"
      >
        <span class="w-2 h-2 rounded-full bg-[#20784d]"></span>
        Inscrits
      </button>
      <button
        on:click={() => dispatch('filterSource', 'osm')}
        class="flex-1 text-xs font-medium px-3 py-1.5 rounded-full transition-all flex items-center justify-center gap-1
              {sourceFilter === 'osm' ? 'bg-[#20784d] text-white shadow-sm' : 'text-gray-600 hover:bg-gray-50'}"
      >
        <span class="w-2 h-2 rounded-full bg-gray-400"></span>
        Google
      </button>
    </div>

    <!-- Filtre distance -->
    {#if userLocation}
      <div class="flex items-center gap-2">
        <div class="relative flex-1">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Icon icon="heroicons:map-pin" class="h-4 w-4 text-gray-400" />
          </div>
          <select
            value={distanceFilter}
            on:change={handleDistanceFilter}
            class="block w-full pl-9 pr-8 py-2 bg-white border border-gray-200 rounded-full text-sm text-gray-700 appearance-none focus:outline-none focus:ring-2 focus:ring-[#20784d]/50 focus:border-[#20784d] transition-all"
          >
            <option value={0}>Toutes distances</option>
            <option value={500}>Moins de 500 m</option>
            <option value={1000}>Moins de 1 km</option>
            <option value={2000}>Moins de 2 km</option>
            <option value={5000}>Moins de 5 km</option>
            <option value={10000}>Moins de 10 km</option>
          </select>
          <div class="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
            <Icon icon="heroicons:chevron-down" class="h-4 w-4 text-gray-400" />
          </div>
        </div>
      </div>
    {/if}

    <div class="text-sm text-gray-600 pt-1 font-medium flex items-center justify-between">
      <span>
        {establishments.length} établissement{establishments.length > 1 ? 's' : ''} trouvé{establishments.length > 1 ? 's' : ''}
      </span>
      {#if distanceFilter > 0 || sourceFilter !== 'all'}
        <button
          on:click={handleClear}
          class="text-xs text-[#20784d] hover:underline font-normal flex items-center gap-1"
        >
          <Icon icon="heroicons:x-mark" class="h-3 w-3" />
          Effacer filtres
        </button>
      {/if}
    </div>
    <div class="text-xs text-gray-400 font-normal mt-0.5">
      🟢 Inscrits · ⚪ Google
    </div>
  </div>

  <!-- Liste des résultats -->
  <div class="flex-1 overflow-y-auto p-4 sm:p-5 bg-gray-50 space-y-3">
    {#if loading}
      <!-- Skeleton : 5 cartes fantômes -->
      <div class="space-y-3">
        {#each Array(5) as _}
          <div class="bg-white p-4 rounded-[2rem] border border-gray-200 animate-pulse">
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 rounded-full bg-gray-200 shrink-0"></div>
              <div class="min-w-0 flex-1 space-y-2">
                <div class="h-4 bg-gray-200 rounded-full w-3/4"></div>
                <div class="h-3 bg-gray-100 rounded-full w-full"></div>
                <div class="h-3 bg-gray-100 rounded-full w-2/3"></div>
                <div class="flex gap-2 mt-3">
                  <div class="h-5 bg-gray-100 rounded-full w-16"></div>
                  <div class="h-5 bg-gray-100 rounded-full w-20"></div>
                </div>
              </div>
              <div class="w-8 h-8 rounded-full bg-gray-100 shrink-0"></div>
            </div>
          </div>
        {/each}
      </div>
    {:else if establishments.length === 0}
      <div class="flex flex-col items-center justify-center h-full text-center p-6 text-gray-500">
        <div class="bg-gray-100 p-4 rounded-full mb-3">
          <Icon icon="heroicons:building-library" class="h-8 w-8 text-gray-400" />
        </div>
        <p class="font-medium text-gray-700">Aucun résultat</p>
        <p class="text-sm mt-1 text-gray-400">Essayez de modifier vos filtres de recherche.</p>
      </div>
    {:else}
      {#if loadingGoogle}
        <div class="flex items-center gap-3 p-3 bg-gray-100 border border-gray-200 rounded-2xl text-sm text-gray-600 animate-pulse">
          <div class="animate-spin rounded-full h-4 w-4 border-2 border-gray-300 border-t-gray-600 shrink-0"></div>
          <span>Recherche d'écoles autour de vous…</span>
        </div>
      {/if}
      {#each establishments as establishment}
        <div
          class="p-4 rounded-[2rem] border cursor-pointer transition-all duration-200 group relative overflow-hidden {selectedId != null && String(establishment.id) === String(selectedId) ? 'bg-green-50 border-[#20784d] shadow-md ring-2 ring-[#20784d]/20' : 'bg-white border-gray-200 hover:border-green-600'}"
          on:click={() => handleSelect(establishment)}
        >
          <div class="absolute left-0 top-0 bottom-0 w-1 transition-colors {selectedId != null && String(establishment.id) === String(selectedId) ? 'bg-[#20784d]' : 'bg-transparent group-hover:bg-[#20784d]'}"></div>
          <div class="flex items-start gap-3">
            {#if establishment.profileImage}
              <img
                src={establishment.profileImage}
                alt={establishment.name}
                class="w-10 h-10 rounded-full object-cover border-2 border-white shadow-sm shrink-0"
              />
            {:else if establishment.source === 'osm'}
              <div class="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center shrink-0">
                <Icon icon="heroicons:globe-alt" class="h-5 w-5 text-gray-500" />
              </div>
            {:else}
              <div class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center shrink-0">
                <Icon icon="heroicons:building-office-2" class="h-5 w-5 text-green-600" />
              </div>
            {/if}

            <div class="min-w-0 flex-1">
              <h3 class="font-medium transition-colors line-clamp-1 {selectedId != null && String(establishment.id) === String(selectedId) ? 'text-[#20784d]' : 'text-gray-900 group-hover:text-[#20784d]'}">
                {establishment.name}
              </h3>
              <p class="text-xs mt-1 flex items-start gap-1 {establishment.address ? 'text-gray-500' : 'text-gray-400 italic'}">
                <Icon icon="heroicons:map-pin" class="h-3.5 w-3.5 shrink-0 mt-0.5 {establishment.address ? 'text-gray-400' : 'text-gray-300'}" />
                <span class="line-clamp-2">
                  {establishment.address || 'Adresse non renseignée'}
                </span>
              </p>

              <div class="flex flex-wrap items-center mt-3 gap-2">
                <!-- Badge source -->
                {#if establishment.source === 'osm'}
                  <span class="text-[10px] font-semibold uppercase tracking-wider px-2 py-1 bg-gray-100 text-gray-600 rounded-full flex items-center gap-1">
                    <Icon icon="heroicons:globe-alt" class="h-3 w-3" />
                    Google
                  </span>
                {:else}
                  <span class="text-[10px] font-semibold uppercase tracking-wider px-2 py-1 bg-[#20784d]/10 text-[#20784d] rounded-full flex items-center gap-1">
                    <Icon icon="heroicons:check-badge" class="h-3 w-3" />
                    Inscrit
                  </span>
                {/if}

                <!-- Type (seulement pour les inscrits) -->
                {#if establishment.source !== 'osm'}
                  <span class="text-[10px] font-semibold uppercase tracking-wider px-2 py-1 bg-gray-100 text-gray-600 rounded-full">
                    {typeLabels[establishment.type] || establishment.type}
                  </span>
                {/if}

                <!-- Distance -->
                 {#if userLocation}
                    <span
                      class="text-xs font-medium text-[#20784d] bg-green-50 px-2 py-1 rounded-full flex items-center gap-1"
                      title="Distance entre votre position et cet établissement"
                    >
                      <Icon icon="heroicons:map-pin" class="h-3 w-3" />
                      À {formatDistance(getEstablishmentDistance(establishment))} de vous
                    </span>
                  {:else}
                    <span class="text-xs font-medium text-gray-500 bg-gray-50 px-2 py-1 rounded-full flex items-center gap-1">
                      <Icon icon="heroicons:map-pin" class="h-3 w-3" />
                      Activez la géolocalisation
                    </span>
                  {/if}
              </div>
            </div>

            <div class="shrink-0">
              <button
                class="h-8 w-8 rounded-full flex items-center justify-center transition-all shadow-sm {selectedId != null && String(establishment.id) === String(selectedId) ? 'bg-[#20784d] text-white' : 'bg-gray-50 text-gray-400 group-hover:bg-[#20784d] group-hover:text-white'}"
                on:click={(e) => { e.stopPropagation(); handleSelect(establishment); }}
                title="Voir sur la carte"
              >
                <Icon icon="heroicons:chevron-right" class="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      {/each}
    {/if}
  </div>
</div>