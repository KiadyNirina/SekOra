<script>
  import Icon from '@iconify/svelte';
  import { page } from '$app/state';
  import { user } from '$lib/stores';

  export let onClose;

  let baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  const navigation = [
    { name: 'Tableau de bord', icon: 'heroicons:home', href: '/etablissement/dashboard' },
    { name: 'Années scolaires', icon: 'heroicons:calendar-days', href: '/etablissement/annees-scolaires' },
    { name: 'Matières', icon: 'heroicons:book-open', href: '/etablissement/matieres' },
    { name: 'Classes', icon: 'heroicons:academic-cap', href: '/etablissement/classes', badge: 'new' },
    { name: 'Étudiants', icon: 'heroicons:user-group', href: '/etablissement/etudiants' },
    { name: 'Professeurs', icon: 'heroicons:academic-cap', href: '/etablissement/professeurs' },
    { name: 'Cours & Emploi du temps', icon: 'heroicons:calendar', href: '/etablissement/cours' },
    { name: 'Notes & Évaluations', icon: 'mdi:clipboard-list-outline', href: '/etablissement/notes' },
    { name: 'Inscriptions', icon: 'heroicons:clipboard-document-check', href: '/etablissement/inscriptions' },
    { name: 'Communication', icon: 'heroicons:chat-bubble-left-right', href: '/etablissement/communication' },
    { name: 'Finances', icon: 'heroicons:currency-dollar', href: '/etablissement/finances' },
    { name: 'Documents', icon: 'heroicons:folder', href: '/etablissement/documents' },
    { name: 'Paramètres', icon: 'heroicons:cog', href: '/etablissement/parametres' }
  ];
</script>

<div class="flex flex-col h-full bg-white">
  <!-- Logo + bouton fermer -->
  <div class="flex items-center h-16 flex-shrink-0 px-4 border-b border-gray-100">
    <img src="/icons/logo.png" class="h-10" alt="Logo" />

    {#if onClose}
      <button
        on:click={onClose}
        class="ml-auto p-2 rounded-lg text-gray-500 hover:text-[#20784d] hover:bg-green-50 focus:outline-none transition-colors"
        aria-label="Fermer le menu"
      >
        <Icon icon="heroicons:x-mark" class="h-5 w-5" />
      </button>
    {/if}
  </div>

  <!-- Navigation -->
  <div class="flex-1 overflow-y-auto">
    <nav class="px-2 py-4 space-y-1">
      {#each navigation as item}
        <a
          href={item.href}
          on:click={() => onClose?.()}
          class="group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors
          {page.url.pathname === item.href
            ? 'bg-green-100 text-[#20784d]'
            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}"
        >
          <Icon
            icon={item.icon}
            class="mr-3 flex-shrink-0 h-5 w-5
            {page.url.pathname === item.href
              ? 'text-[#20784d]'
              : 'text-gray-400 group-hover:text-gray-500'}"
          />
          <span class="flex-1 truncate">{item.name}</span>
          {#if item.badge}
            <span class="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              {item.badge}
            </span>
          {/if}
        </a>
      {/each}
    </nav>
  </div>

  <!-- User Profile -->
  <div class="flex-shrink-0 border-t border-gray-100 p-4">
    {#if $user}
      <div class="flex items-center">
        <div class="h-9 w-9 rounded-full bg-green-100 flex items-center justify-center overflow-hidden flex-shrink-0">
          {#if $user.profile?.user?.profile_image}
            <img src="{$user.profile.user.profile_image}" class="h-9 w-9 object-cover" alt="" />
          {:else}
            <Icon icon="heroicons:user-circle" class="h-6 w-6 text-green-600" />
          {/if}
        </div>

        <div class="ml-3 min-w-0 flex-1">
          <p class="text-sm font-medium text-gray-700 truncate">
            {$user.first_name
              ? `${$user.first_name} ${$user.last_name}`
              : $user.username || 'Utilisateur'}
          </p>

          <a
            href="/etablissement/profil"
            on:click={() => onClose?.()}
            class="text-xs font-medium text-[#20784d] hover:text-green-600"
          >
            Voir profil
          </a>
        </div>
      </div>
    {:else}
      <div class="flex items-center">
        <div class="h-9 w-9 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
          <Icon icon="heroicons:user-circle" class="h-6 w-6 text-green-600" />
        </div>
        <div class="ml-3">
          <p class="text-sm font-medium text-gray-500">Chargement...</p>
        </div>
      </div>
    {/if}
  </div>
</div>