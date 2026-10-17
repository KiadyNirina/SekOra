<script>
  import Sidebar from '../../components/etablissement/Sidebar.svelte';
  import Header from '../../components/etablissement/Header.svelte';
  import SetupBanner from '../../components/etablissement/SetupBanner.svelte';
  import { fade, fly } from 'svelte/transition';

  let sidebarOpen = false;
</script>

<div class="flex h-screen bg-gray-50">
  <!-- Sidebar desktop -->
  <div class="hidden md:flex md:flex-shrink-0">
    <div class="flex flex-col w-72 border-r border-gray-200 bg-white">
      <Sidebar />
    </div>
  </div>

  <!-- Overlay mobile -->
  {#if sidebarOpen}
    <div
      transition:fade={{ duration: 200 }}
      class="fixed inset-0 bg-black/50 z-40 md:hidden"
      on:click={() => sidebarOpen = false}
      on:keydown={(e) => e.key === 'Escape' && (sidebarOpen = false)}
      role="button"
      tabindex="0"
      aria-label="Fermer le menu"
    ></div>
  {/if}

  <!-- Drawer mobile -->
  {#if sidebarOpen}
    <div
      transition:fly={{ x: -300, duration: 250 }}
      class="fixed inset-y-0 left-0 z-50 w-72 bg-white border-r border-gray-200 md:hidden overflow-y-auto"
    >
      <Sidebar onClose={() => sidebarOpen = false} />
    </div>
  {/if}

  <div class="flex flex-col flex-1 overflow-hidden">
    <Header onToggleSidebar={() => sidebarOpen = !sidebarOpen} />
    <SetupBanner />

    <main class="flex-1 overflow-y-auto p-4 md:p-6 bg-gray-50">
      <slot />
    </main>
  </div>
</div>