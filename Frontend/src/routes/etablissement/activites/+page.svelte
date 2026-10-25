<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import Icon from '@iconify/svelte';
  import { authApi } from '$lib/api';

  // ---------- State ----------
  let activities = [];
  let countsByType = { new_student: 0, new_teacher: 0, new_class: 0, grade: 0 };
  let loading = true;
  let error = null;

  let pagination = {
    page: 1,
    page_size: 20,
    total_pages: 1,
    count: 0,
  };

  // ---------- Filtres ----------
  let filterType = '';
  let searchTerm = '';
  let filterDays = 90;

  // Debounce pour la recherche
  let searchTimer;

  // ---------- Types ----------
  const TYPE_OPTIONS = [
    { value: '', label: 'Tout', icon: 'heroicons:squares-2x2' },
    { value: 'new_student', label: 'Élèves', icon: 'heroicons:user-plus' },
    { value: 'new_teacher', label: 'Professeurs', icon: 'heroicons:academic-cap' },
    { value: 'new_class', label: 'Classes', icon: 'heroicons:building-library' },
    { value: 'grade', label: 'Évaluations', icon: 'heroicons:clipboard-document-check' },
  ];

  const activityIcons = {
    new_student: 'heroicons:user-plus',
    new_teacher: 'heroicons:academic-cap',
    new_class: 'heroicons:building-library',
    grade: 'heroicons:clipboard-document-check',
    payment: 'heroicons:currency-dollar',
    absence: 'heroicons:exclamation-triangle',
  };

  const activityColors = {
    new_student: 'text-green-600 bg-green-100 ring-green-200',
    new_teacher: 'text-indigo-600 bg-indigo-100 ring-indigo-200',
    new_class: 'text-purple-600 bg-purple-100 ring-purple-200',
    grade: 'text-blue-600 bg-blue-100 ring-blue-200',
    payment: 'text-emerald-600 bg-emerald-100 ring-emerald-200',
    absence: 'text-amber-600 bg-amber-100 ring-amber-200',
  };

  // ---------- Sync URL ----------
  function syncFromUrl() {
    filterType = $page.url.searchParams.get('type') || '';
    searchTerm = $page.url.searchParams.get('search') || '';
    filterDays = parseInt($page.url.searchParams.get('days') || '90');
    pagination.page = parseInt($page.url.searchParams.get('page') || '1');
  }

  function updateUrl() {
    const params = new URLSearchParams();
    if (filterType) params.set('type', filterType);
    if (searchTerm) params.set('search', searchTerm);
    if (filterDays !== 90) params.set('days', String(filterDays));
    if (pagination.page > 1) params.set('page', String(pagination.page));

    const qs = params.toString();
    goto(`?${qs}`, { replaceState: true, keepFocus: true, noScroll: true });
  }

  // ---------- Data loading ----------
  async function loadActivities() {
    loading = true;
    error = null;
    try {
      const data = await authApi.getActivities({
        type: filterType || undefined,
        search: searchTerm || undefined,
        days: filterDays,
        page: pagination.page,
        page_size: pagination.page_size,
      });

      activities = data.results || [];
      countsByType = data.counts_by_type || countsByType;
      pagination = {
        page: data.page,
        page_size: data.page_size,
        total_pages: data.total_pages,
        count: data.count,
      };
    } catch (err) {
      error = err.message || 'Impossible de charger les activités';
      console.error(err);
    } finally {
      loading = false;
    }
  }

  function handleFilterChange() {
    pagination.page = 1;
    updateUrl();
    loadActivities();
  }

  function handleSearchInput() {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      pagination.page = 1;
      updateUrl();
      loadActivities();
    }, 350);
  }

  function goToPage(n) {
    if (n < 1 || n > pagination.total_pages) return;
    pagination.page = n;
    updateUrl();
    loadActivities();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function getIcon(type) {
    return activityIcons[type] || 'heroicons:information-circle';
  }

  function getColor(type) {
    return activityColors[type] || 'text-gray-600 bg-gray-100 ring-gray-200';
  }

  function getMessage(activity) {
    switch (activity.type) {
      case 'new_student':
        return `Nouvel élève : ${activity.name} (${activity.class})`;
      case 'new_teacher':
        return `Nouveau professeur : ${activity.name}`;
      case 'new_class':
        return `Nouvelle classe : ${activity.name}`;
      case 'grade':
        return `Évaluation publiée : ${activity.name}`;
      case 'payment':
        return `Paiement reçu : ${activity.name}`;
      case 'absence':
        return `Absence signalée : ${activity.name}`;
      default:
        return activity.name || 'Activité';
    }
  }

  onMount(() => {
    syncFromUrl();
    loadActivities();
  });

  // Recharge quand l'URL change (bouton retour navigateur)
  $: if ($page.url.searchParams.toString()) {
    const currentPage = parseInt($page.url.searchParams.get('page') || '1');
    if (currentPage !== pagination.page) {
      syncFromUrl();
      loadActivities();
    }
  }

  // ---------- Pagination helper ----------
  $: visiblePages = (() => {
    const total = pagination.total_pages;
    const current = pagination.page;
    const pages = [];
    const maxVisible = 5;
    let start = Math.max(1, current - Math.floor(maxVisible / 2));
    let end = Math.min(total, start + maxVisible - 1);

    if (end - start + 1 < maxVisible) {
      start = Math.max(1, end - maxVisible + 1);
    }

    for (let i = start; i <= end; i++) {
      if (i === 1 || i === total || (i >= start && i <= end)) {
        pages.push(i);
      }
    }
    return pages;
  })();
</script>

<svelte:head>
  <title>Activités — Établissement</title>
</svelte:head>

<div class="mx-auto space-y-6">

  <!-- Header -->
  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
        <Icon icon="heroicons:clock" class="h-7 w-7 text-[#20784d]" />
        Activités récentes
      </h1>
      <p class="mt-1 text-sm text-gray-500">
        Historique des {pagination.count} dernières activités de votre établissement
        {#if filterDays !== 90}
          (sur {filterDays} jours)
        {/if}
      </p>
    </div>
    <button
      on:click={loadActivities}
      disabled={loading}
      class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
    >
      <Icon icon="heroicons:arrow-path" class={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
      Rafraîchir
    </button>
  </div>

  <!-- Filtres -->
  <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-4 space-y-4">

    <!-- Tabs type -->
    <div class="flex flex-wrap gap-2">
      {#each TYPE_OPTIONS as opt}
        <button
          on:click={() => { filterType = opt.value; handleFilterChange(); }}
          class="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-full transition-colors
          {filterType === opt.value
            ? 'bg-[#20784d] text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
        >
          <Icon icon={opt.icon} class="h-3.5 w-3.5" />
          {opt.label}
          {#if opt.value && countsByType[opt.value] !== undefined}
            <span class="ml-1 px-1.5 py-0.5 text-[10px] rounded-full
              {filterType === opt.value ? 'bg-white/20' : 'bg-gray-300/50'}">
              {countsByType[opt.value]}
            </span>
          {/if}
        </button>
      {/each}
    </div>

    <!-- Recherche + fenêtre -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
      <div class="sm:col-span-2">
        <label for="search" class="block text-xs font-medium text-gray-700 mb-1">
          Recherche
        </label>
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Icon icon="heroicons:magnifying-glass" class="h-4 w-4 text-gray-400" />
          </div>
          <input
            id="search"
            type="text"
            bind:value={searchTerm}
            on:input={handleSearchInput}
            placeholder="Rechercher une activité..."
            class="block w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#20784d]/30 focus:border-[#20784d]"
          />
        </div>
      </div>

      <div>
        <label for="days" class="block text-xs font-medium text-gray-700 mb-1">
          Période
        </label>
        <select
          id="days"
          bind:value={filterDays}
          on:change={handleFilterChange}
          class="block w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#20784d]/30 focus:border-[#20784d]"
        >
          <option value={7}>7 derniers jours</option>
          <option value={30}>30 derniers jours</option>
          <option value={90}>90 derniers jours</option>
          <option value={180}>6 derniers mois</option>
          <option value={365}>1 an</option>
        </select>
      </div>
    </div>
  </div>

  <!-- Contenu -->
  {#if loading}
    <!-- Skeleton -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm divide-y divide-gray-100">
      {#each Array(5) as _}
        <div class="p-4 animate-pulse">
          <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-full bg-gray-200"></div>
            <div class="flex-1 space-y-2">
              <div class="h-3 bg-gray-200 rounded w-3/4"></div>
              <div class="h-2 bg-gray-200 rounded w-1/3"></div>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {:else if error}
    <div class="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
      <Icon icon="heroicons:exclamation-circle" class="h-10 w-10 text-red-500 mx-auto mb-3" />
      <p class="text-sm text-red-800 mb-3">{error}</p>
      <button
        on:click={loadActivities}
        class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700"
      >
        Réessayer
      </button>
    </div>
  {:else if activities.length === 0}
    <!-- Empty state -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-12 text-center">
      <div class="mx-auto w-14 h-14 rounded-full bg-gray-100 flex items-center justify-center mb-4">
        <Icon icon="heroicons:clock" class="h-7 w-7 text-gray-400" />
      </div>
      <h3 class="text-base font-semibold text-gray-900">Aucune activité</h3>
      <p class="mt-1 text-sm text-gray-500">
        {#if searchTerm || filterType}
          Aucune activité ne correspond à vos filtres.
        {:else}
          Aucune activité enregistrée sur cette période.
        {/if}
      </p>
      {#if searchTerm || filterType}
        <button
          on:click={() => { filterType = ''; searchTerm = ''; handleFilterChange(); }}
          class="mt-4 text-sm font-medium text-[#20784d] hover:text-green-600"
        >
          Effacer les filtres
        </button>
      {/if}
    </div>
  {:else}
    <!-- Timeline des activités -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      <ul class="divide-y divide-gray-100">
        {#each activities as activity, i (activity.date + i)}
          <li class="hover:bg-gray-50 transition-colors">
            <a
              href={activity.link || '#'}
              class="flex items-center gap-4 px-5 py-4 group"
            >
              <!-- Icône -->
              <div class={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ring-2 ${getColor(activity.type)}`}>
                <Icon icon={getIcon(activity.type)} class="h-5 w-5" />
              </div>

              <!-- Message -->
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate group-hover:text-[#20784d] transition-colors">
                  {getMessage(activity)}
                </p>
                <p class="text-xs text-gray-500 mt-0.5">
                  {activity.time || activity.date}
                </p>
              </div>

              <!-- Chevron -->
              <Icon
                icon="heroicons:chevron-right"
                class="h-5 w-5 text-gray-300 group-hover:text-[#20784d] transition-colors flex-shrink-0"
              />
            </a>
          </li>
        {/each}
      </ul>

      <!-- Pagination -->
      {#if pagination.total_pages > 1}
        <div class="border-t border-gray-100 px-5 py-4 flex items-center justify-between flex-wrap gap-3">
          <p class="text-sm text-gray-600">
            Page <span class="font-semibold text-gray-900">{pagination.page}</span>
            sur <span class="font-semibold text-gray-900">{pagination.total_pages}</span>
            · {pagination.count} activité{pagination.count > 1 ? 's' : ''}
          </p>

          <div class="flex items-center gap-1">
            <button
              on:click={() => goToPage(pagination.page - 1)}
              disabled={pagination.page <= 1}
              class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              aria-label="Page précédente"
            >
              <Icon icon="heroicons:chevron-left" class="h-4 w-4" />
            </button>

            {#each visiblePages as p (p)}
              <button
                on:click={() => goToPage(p)}
                class="min-w-[2rem] h-8 px-2 rounded-lg text-sm font-medium transition-colors
                {p === pagination.page
                  ? 'bg-[#20784d] text-white'
                  : 'text-gray-700 hover:bg-gray-100'}"
              >
                {p}
              </button>
            {/each}

            <button
              on:click={() => goToPage(pagination.page + 1)}
              disabled={pagination.page >= pagination.total_pages}
              class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              aria-label="Page suivante"
            >
              <Icon icon="heroicons:chevron-right" class="h-4 w-4" />
            </button>
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>