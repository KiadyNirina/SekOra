<script>
  import Icon from '@iconify/svelte';
  import { createEventDispatcher } from 'svelte';

  export let activities = [];
  export let loading = false;
  export let error = null;
  export let viewAllHref = '/etablissement/activites';

  const dispatch = createEventDispatcher();

  const activityIcons = {
    new_student: 'heroicons:user-plus',
    new_teacher: 'heroicons:academic-cap',
    new_class: 'heroicons:building-library',
    grade: 'heroicons:clipboard-document-check',
    payment: 'heroicons:currency-dollar',
    absence: 'heroicons:exclamation-triangle',
  };

  const activityColors = {
    new_student: 'text-green-600 bg-green-100',
    new_teacher: 'text-indigo-600 bg-indigo-100',
    new_class: 'text-purple-600 bg-purple-100',
    grade: 'text-blue-600 bg-blue-100',
    payment: 'text-emerald-600 bg-emerald-100',
    absence: 'text-amber-600 bg-amber-100',
  };

  function getIcon(type) {
    return activityIcons[type] || 'heroicons:information-circle';
  }

  function getColor(type) {
    return activityColors[type] || 'text-gray-600 bg-gray-100';
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
</script>

<div class="bg-white shadow rounded-lg overflow-hidden">
  <!-- Header avec bouton refresh -->
  <div class="px-4 py-5 sm:px-6 border-b border-gray-200 flex items-center justify-between">
    <h3 class="text-lg leading-6 font-medium text-gray-900">Activités récentes</h3>
    <button
      on:click={() => dispatch('refresh')}
      disabled={loading}
      class="p-1.5 rounded-lg text-gray-400 hover:text-[#20784d] hover:bg-green-50 transition-colors disabled:opacity-50"
      title="Rafraîchir"
    >
      <Icon icon="heroicons:arrow-path" class={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
    </button>
  </div>

  {#if error}
    <div class="px-4 py-6 text-center">
      <Icon icon="heroicons:exclamation-circle" class="h-8 w-8 text-red-400 mx-auto mb-2" />
      <p class="text-sm text-red-700">{error}</p>
    </div>
  {:else if loading}
    <div class="divide-y divide-gray-200">
      {#each Array(3) as _}
        <div class="px-4 py-4 sm:px-6 animate-pulse">
          <div class="flex items-center gap-3">
            <div class="h-9 w-9 rounded-full bg-gray-200"></div>
            <div class="flex-1 space-y-2">
              <div class="h-3 bg-gray-200 rounded w-3/4"></div>
              <div class="h-2 bg-gray-200 rounded w-1/4"></div>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {:else if activities.length === 0}
    <!-- Empty state -->
    <div class="py-10 text-center">
      <div class="mx-auto w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mb-3">
        <Icon icon="heroicons:clock" class="h-6 w-6 text-gray-400" />
      </div>
      <p class="text-sm text-gray-500">Aucune activité récente</p>
    </div>
  {:else}
    <div class="divide-y divide-gray-200">
      {#each activities as activity}
        <div class="px-4 py-4 sm:px-6 hover:bg-gray-50 transition-colors">
          <div class="flex items-center gap-3">
            <div class={`flex-shrink-0 rounded-full p-2 ${getColor(activity.type)}`}>
              <Icon icon={getIcon(activity.type)} class="h-5 w-5" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">
                {getMessage(activity)}
              </p>
              <p class="text-xs text-gray-500 mt-0.5">{activity.time || activity.date}</p>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}

  <div class="bg-gray-50 px-4 py-3 sm:px-6">
    <a
      href={viewAllHref}
      class="text-sm font-medium text-[#20784d] hover:text-green-600"
    >
      Voir toutes les activités →
    </a>
  </div>
</div>