<script>
  import Icon from '@iconify/svelte';
  import { fly } from 'svelte/transition';
  import { createEventDispatcher } from 'svelte';

  export let message = '';
  export let type = 'success'; // success | error | info
  export let duration = 3500;

  const dispatch = createEventDispatcher();

  const styles = {
    success: { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-800', icon: 'heroicons:check-circle', iconColor: 'text-green-600' },
    error:   { bg: 'bg-red-50',   border: 'border-red-200',   text: 'text-red-800',   icon: 'heroicons:x-circle',     iconColor: 'text-red-600' },
    info:    { bg: 'bg-blue-50',  border: 'border-blue-200',  text: 'text-blue-800',  icon: 'heroicons:information-circle', iconColor: 'text-blue-600' }
  };

  let timer;

  $: if (message) {
    clearTimeout(timer);
    timer = setTimeout(() => dispatch('close'), duration);
  }
</script>

{#if message}
  <div
    transition:fly={{ y: -20, duration: 250 }}
    class="fixed top-4 right-4 z-[60] max-w-md rounded-lg border shadow-lg px-4 py-3 flex items-start gap-3 {styles[type].bg} {styles[type].border}"
  >
    <Icon icon={styles[type].icon} class="h-5 w-5 flex-shrink-0 mt-0.5 {styles[type].iconColor}" />
    <p class="text-sm font-medium flex-1 {styles[type].text}">{message}</p>
    <button
      on:click={() => dispatch('close')}
      class="text-gray-400 hover:text-gray-600 flex-shrink-0"
      aria-label="Fermer"
    >
      <Icon icon="heroicons:x-mark" class="h-4 w-4" />
    </button>
  </div>
{/if}