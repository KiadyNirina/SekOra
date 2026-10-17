<!-- src/lib/components/register/GoogleMapsGuidePopup.svelte -->
<script>
  import Icon from '@iconify/svelte';

  export let show = false;

  function close() {
    show = false;
  }

  function openGoogleMaps() {
    window.open('https://www.google.com/maps', '_blank');
  }
</script>

{#if show}
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fadeIn">
    <div class="relative w-full max-w-lg bg-white rounded-[2rem] overflow-hidden animate-slideUp">
      <!-- En-tête du popup -->
      <div class="bg-green-600 px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <Icon icon="logos:google-maps" class="h-6 w-6 text-white" />
            <div>
              <h3 class="text-lg font-semibold text-white">Guide Google Maps</h3>
              <p class="text-xs text-blue-100">Obtenez les coordonnées GPS</p>
            </div>
          </div>
          <button
            on:click={close}
            class="text-white/80 hover:text-white transition-colors p-1 rounded-full hover:bg-white/20"
          >
            <Icon icon="heroicons:x-mark" class="h-6 w-6" />
          </button>
        </div>
      </div>

      <!-- Corps du popup -->
      <div class="p-6 max-h-[70vh] overflow-y-auto">
        <div class="space-y-3">
          <div class="flex items-center gap-3 p-1">
            <div class="flex-shrink-0 w-8 h-8 bg-green-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
              1
            </div>
            <p class="text-sm text-gray-700">Ouvrez <strong>Google Maps</strong> dans votre navigateur</p>
          </div>

          <div class="flex items-center gap-3 p-1">
            <div class="flex-shrink-0 w-8 h-8 bg-green-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
              2
            </div>
            <p class="text-sm text-gray-700">Recherchez l'adresse ou faites un <strong>clic droit</strong> sur le lieu</p>
          </div>

          <div class="flex items-center gap-3 p-1">
            <div class="flex-shrink-0 w-8 h-8 bg-green-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
              3
            </div>
            <p class="text-sm text-gray-700">Cliquez sur les coordonnées affichées pour les copier</p>
          </div>

          <div class="mt-4 p-4 bg-gray-50 rounded-[2rem] border border-gray-200">
            <p class="text-xs text-gray-600 mb-2">📝 Exemple de coordonnées :</p>
            <div class="grid grid-cols-2 gap-2 text-xs font-mono">
              <div class="bg-white p-2 rounded-full border border-gray-200">
                <span class="text-gray-500">Latitude :</span>
                <span class="text-green-600 font-semibold">-18.8792</span>
              </div>
              <div class="bg-white p-2 rounded-full border border-gray-200">
                <span class="text-gray-500">Longitude :</span>
                <span class="text-green-600 font-semibold">47.5079</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pied du popup -->
      <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex flex-col sm:flex-row gap-3 justify-end">
        <button
          on:click={close}
          class="w-full sm:w-auto px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-full hover:bg-gray-50 transition-colors"
        >
          Fermer
        </button>
        <button
          on:click={openGoogleMaps}
          class="w-full sm:w-auto px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-full hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
        >
          <Icon icon="logos:google-maps" class="h-4 w-4" />
          Ouvrir Google Maps
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  @keyframes slideUp {
    from {
      transform: translateY(20px) scale(0.95);
      opacity: 0;
    }
    to {
      transform: translateY(0) scale(1);
      opacity: 1;
    }
  }

  .animate-fadeIn {
    animation: fadeIn 0.3s ease-out;
  }

  .animate-slideUp {
    animation: slideUp 0.3s ease-out;
  }
</style>