<script>
    import Icon from '@iconify/svelte';
    import { fade } from 'svelte/transition';
    import { goto } from '$app/navigation';
  
    let menuOpen = false;
</script>

<nav class="bg-white sticky top-0 z-50">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between h-16">
      <div class="flex items-center">
        <a href="/" class="flex items-center">
          <Icon icon="fluent:school-24-filled" class="h-8 w-8 text-[#20784d]" />
          <img src="/icons/logo.png" class="h-10" alt="">
        </a>
      </div>
      
      <div class="hidden md:flex items-center space-x-8">
        <a href="#features" class="text-gray-700 hover:text-[#20784d] px-3 py-2 text-base font-medium">Fonctionnalités</a>
      </div>
      
      <div class="hidden md:flex items-center space-x-4">
        <button 
          on:click={() => goto('/map')}
          class="flex items-center gap-2 bg-green-50 text-[#20784d] hover:cursor-pointer px-4 py-2 rounded-full text-base font-medium transition-all duration-200 border border-green-200 hover:border-green-600"
          title="Rechercher des établissements"
        >
          <Icon icon="heroicons:magnifying-glass" class="h-5 w-5" />
          <span>Rechercher</span>
        </button>
        
        <a href="/login" class="bg-[#20784d] text-white px-4 py-2 rounded-full text-base font-medium hover:bg-green-700 transition-colors">Connexion</a>
      </div>
      
      <div class="md:hidden flex items-center">
        <button 
          on:click={() => menuOpen = !menuOpen} 
          class="p-2 rounded-lg text-gray-500 hover:text-[#20784d] hover:bg-green-50 transition-colors focus:outline-none"
          aria-label="Menu"
        >
          <Icon icon={menuOpen ? 'heroicons-outline:x' : 'heroicons-outline:menu'} class="h-6 w-6" />
        </button>
      </div>
    </div>
  </div>
  
  {#if menuOpen}
    <div transition:fade class="md:hidden bg-white border-t border-gray-100 shadow-lg">
      <div class="px-4 pt-3 pb-4 space-y-1">
        <a 
          href="#features" 
          class="flex items-center gap-3 px-3 py-3 text-base font-medium text-gray-700 rounded-lg hover:text-[#20784d] hover:bg-green-50 transition-colors"
          on:click={() => menuOpen = false}
        >
          <Icon icon="heroicons-outline:sparkles" class="h-5 w-5 text-[#20784d]" />
          Fonctionnalités
        </a>
        
        <a 
          href="/map" 
          class="flex items-center gap-3 px-3 py-3 text-base font-medium text-gray-700 rounded-lg hover:text-[#20784d] hover:bg-green-50 transition-colors"
          on:click={() => menuOpen = false}
        >
          <Icon icon="heroicons:magnifying-glass" class="h-5 w-5 text-[#20784d]" />
          Rechercher des établissements
        </a>
        
        <div class="pt-3 mt-2 border-t border-gray-100 space-y-2">
          <a 
            href="/login" 
            class="flex items-center justify-center gap-3 w-full px-4 py-3 text-base font-medium text-[#20784d] bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors"
            on:click={() => menuOpen = false}
          >
            <Icon icon="heroicons-outline:login" class="h-5 w-5" />
            Connexion
          </a>
        </div>
      </div>
    </div>
  {/if}
</nav>