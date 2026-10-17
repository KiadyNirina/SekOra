<!-- src/lib/components/register/UserTypeSelector.svelte -->
<script>
  import Icon from '@iconify/svelte';
  import { createEventDispatcher } from 'svelte';

  export let userTypes = [];
  export let selectedType = null;

  const dispatch = createEventDispatcher();

  function selectType(type) {
    // Ne rien faire si indisponible
    if (type.available === false) return;
    dispatch('select', type.id);
  }

  function goToForm() {
    dispatch('next');
  }
</script>

<div class="animate-fadeIn">
  <h3 class="text-lg font-medium text-gray-900 mb-6 text-center">Je suis...</h3>

  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
    {#each userTypes as type}
      <button
        type="button"
        on:click={() => selectType(type)}
        disabled={type.available === false}
        class={`p-6 rounded-[2rem] border-2 text-left transition-all duration-300 ${
          type.available === false
            ? 'border-gray-200 bg-gray-50 opacity-70 cursor-not-allowed'
            : selectedType === type.id
              ? 'border-green-500 bg-green-50 transform hover:scale-[1.02]'
              : 'border-gray-200 hover:border-green-300 hover:bg-gray-50 transform hover:scale-[1.02]'
        }`}
      >
        <div class="flex items-start gap-4">
          <div class={`p-3 rounded-full ${
            selectedType === type.id && type.available !== false
              ? 'bg-green-100 text-green-600'
              : 'bg-gray-100 text-gray-600'
          }`}>
            <Icon icon={type.icon} class="h-6 w-6" />
          </div>
          <div class="flex-1">
            <div class="flex items-center gap-2 flex-wrap">
              <h4 class={`font-medium ${
                selectedType === type.id && type.available !== false
                  ? 'text-green-700'
                  : 'text-gray-900'
              }`}>
                {type.label}
              </h4>
              {#if type.available === false}
                <span class="text-xs text-gray-500 bg-gray-200 px-2 py-0.5 rounded-full">
                  Bientôt
                </span>
              {/if}
            </div>
            <p class="text-sm text-gray-500 mt-1">{type.description}</p>
          </div>
          {#if selectedType === type.id && type.available !== false}
            <div class="flex-shrink-0">
              <Icon icon="heroicons:check-circle-solid" class="h-6 w-6 text-green-500" />
            </div>
          {/if}
        </div>
      </button>
    {/each}
  </div>

  <div class="flex justify-center">
    <button
      type="button"
      on:click={goToForm}
      disabled={!selectedType}
      class={`inline-flex items-center px-8 py-3 rounded-full text-sm font-medium transition-all duration-300 ${
        selectedType
          ? 'bg-green-600 text-white hover:bg-green-700 transform hover:scale-105'
          : 'bg-gray-200 text-gray-400 cursor-not-allowed'
      }`}
    >
      Suivant
      <Icon icon="heroicons:arrow-right" class="h-5 w-5 ml-2" />
    </button>
  </div>
</div>

<style>
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .animate-fadeIn {
    animation: fadeIn 0.3s ease-out;
  }
</style>