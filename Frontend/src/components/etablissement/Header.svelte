<script>
  import Icon from '@iconify/svelte';
  import { user } from '$lib/stores';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { authApi, authStore } from '$lib/api';

  export let onToggleSidebar;

  let baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  let searchQuery = '';
  let showDropdown = false;
  let showLogoutModal = false;

  function toggleDropdown() {
    showDropdown = !showDropdown;
  }

  function openLogoutModal() {
    showDropdown = false;
    showLogoutModal = true;
  }

  function closeLogoutModal() {
    showLogoutModal = false;
  }

  function handleLogout() {
    authStore.clearTokens();
    user.set(null);
    closeLogoutModal();
    goto('/login');
  }

  function handleMenuClick(e) {
    e.stopPropagation();
    if (onToggleSidebar) onToggleSidebar();
  }

  onMount(() => {
    function handleClickOutside(event) {
      const dropdown = document.querySelector('.profile-dropdown');
      if (dropdown && !dropdown.contains(event.target)) {
        showDropdown = false;
      }
    }
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  });
</script>

<header class="bg-white shadow-sm relative z-30">
  <div class="px-4 py-3 sm:px-6 lg:px-8">
    <div class="flex items-center justify-between gap-3">

      <!-- ✅ BOUTON MENU MOBILE -->
      <button
        type="button"
        class="md:hidden flex-shrink-0 inline-flex items-center justify-center w-10 h-10 rounded-lg text-gray-700 bg-gray-100 hover:bg-green-100 hover:text-[#20784d] active:scale-95 transition-all focus:outline-none focus:ring-2 focus:ring-[#20784d]"
        on:click={handleMenuClick}
        aria-label="Ouvrir le menu"
      >
        <Icon icon="heroicons:bars-3" class="w-6 h-6" />
      </button>

      <!-- Barre de recherche -->
      <div class="flex-1 min-w-0">
        <div class="relative text-gray-400 focus-within:text-gray-500">
          <div class="pointer-events-none absolute inset-y-0 left-0 pl-3 flex items-center">
            <Icon icon="heroicons:magnifying-glass" class="h-5 w-5" />
          </div>
          <input
            id="search"
            name="search"
            class="block w-full bg-gray-50 py-2 pl-10 pr-3 border border-gray-200 rounded-full leading-5 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#20784d] focus:border-[#20784d] focus:bg-white sm:text-sm transition-colors"
            placeholder="Rechercher"
            type="search"
            bind:value={searchQuery}
          />
        </div>
      </div>

      <!-- Actions droite -->
      <div class="flex items-center space-x-1 sm:space-x-2 flex-shrink-0">
        <button class="hidden sm:flex bg-white p-2 rounded-full text-gray-400 hover:text-[#20784d] hover:bg-green-50 focus:outline-none transition-colors">
          <Icon icon="heroicons:bell" class="h-5 w-5" />
        </button>
        <button class="hidden sm:flex bg-white p-2 rounded-full text-gray-400 hover:text-[#20784d] hover:bg-green-50 focus:outline-none transition-colors">
          <Icon icon="heroicons:envelope" class="h-5 w-5" />
        </button>

        <div class="relative profile-dropdown">
          <div
            class="h-9 w-9 rounded-full bg-green-100 flex items-center justify-center cursor-pointer hover:bg-green-200 transition-colors"
            on:click={toggleDropdown}
            on:keydown={(e) => e.key === 'Enter' && toggleDropdown()}
            role="button"
            tabindex="0"
            aria-label="Menu utilisateur"
          >
            {#if $user?.profile?.user?.profile_image}
              <img src="{$user.profile.user.profile_image}" class="h-9 w-9 rounded-full object-cover" alt="Profile Image" />
            {:else}
              <Icon icon="heroicons:user-circle" class="h-6 w-6 text-green-600" />
            {/if}
          </div>

          {#if showDropdown}
            <div class="absolute right-0 mt-2 w-56 bg-white rounded-md shadow-lg py-1 border border-gray-200 z-50">
              <div class="px-4 py-2 border-b border-gray-100">
                <p class="text-sm font-medium text-gray-900 truncate">
                  {$user.first_name
                  ? `${$user.first_name} ${$user.last_name}`
                  : $user.username || 'Utilisateur'}
                </p>
                <p class="text-xs text-gray-500 truncate">{$user?.email || 'email@exemple.com'}</p>
              </div>
              <a href="/etablissement/profil" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors">
                <Icon icon="heroicons:user" class="inline h-4 w-4 mr-2" />
                Mon profil
              </a>
              <a href="/settings" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors">
                <Icon icon="heroicons:cog" class="inline h-4 w-4 mr-2" />
                Paramètres
              </a>
              <button
                on:click={openLogoutModal}
                class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors border-t border-gray-100"
              >
                <Icon icon="heroicons:arrow-right-on-rectangle" class="inline h-4 w-4 mr-2" />
                Se déconnecter
              </button>
            </div>
          {/if}
        </div>
      </div>
    </div>
  </div>
</header>

{#if showLogoutModal}
  <div class="fixed inset-0 z-[100] overflow-y-auto" role="dialog" aria-modal="true">
    <div class="flex items-center justify-center min-h-screen p-4">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75" on:click={closeLogoutModal} role="button" tabindex="-1" aria-label="Fermer"></div>
      <div class="relative bg-white rounded-lg shadow-xl max-w-sm w-full mx-auto p-6 z-10">
        <div class="flex items-start space-x-4">
          <div class="flex-shrink-0">
            <div class="h-10 w-10 rounded-full bg-red-100 flex items-center justify-center">
              <Icon icon="heroicons:exclamation-triangle" class="h-6 w-6 text-red-600" />
            </div>
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-medium text-gray-900">Déconnexion</h3>
            <p class="mt-2 text-sm text-gray-500">Êtes-vous sûr de vouloir vous déconnecter ?</p>
          </div>
        </div>
        <div class="mt-6 flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-3 space-y-3 sm:space-y-0">
          <button type="button" class="w-full sm:w-auto px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50" on:click={closeLogoutModal}>
            Annuler
          </button>
          <button type="button" class="w-full sm:w-auto px-4 py-2 bg-red-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-red-700" on:click={handleLogout}>
            Se déconnecter
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}