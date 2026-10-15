<script>
  import Icon from '@iconify/svelte';
  import { fade, scale } from 'svelte/transition';
  import { createEventDispatcher } from 'svelte';

  export let open = false;
  export let title = '';
  export let size = 'md'; // sm | md | lg | xl
  export let closeOnBackdrop = true;

  const dispatch = createEventDispatcher();

  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl'
  };

  function close() {
    dispatch('close');
  }

  function handleBackdrop() {
    if (closeOnBackdrop) close();
  }

  function handleKeydown(e) {
    if (e.key === 'Escape') close();
  }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if open}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center p-4"
    role="dialog"
    aria-modal="true"
  >
    <div
      transition:fade={{ duration: 150 }}
      class="absolute inset-0 bg-black/50"
      on:click={handleBackdrop}
      on:keydown={() => {}}
      role="button"
      tabindex="-1"
      aria-label="Fermer"
    ></div>

    <div
      transition:scale={{ duration: 200, start: 0.95 }}
      class="relative w-full {sizes[size]} bg-white rounded-xl shadow-xl overflow-hidden"
    >
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
        <h3 class="text-lg font-semibold text-gray-900">{title}</h3>
        <button
          on:click={close}
          class="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors"
          aria-label="Fermer"
        >
          <Icon icon="heroicons:x-mark" class="h-5 w-5" />
        </button>
      </div>

      <div class="p-5">
        <slot />
      </div>

      {#if $$slots.footer}
        <div class="px-5 py-4 bg-gray-50 border-t border-gray-100 flex justify-end gap-2">
          <slot name="footer" />
        </div>
      {/if}
    </div>
  </div>
{/if}