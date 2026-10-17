<script>
  import Icon from '@iconify/svelte';
  import Modal from './Modal.svelte';
  import { createEventDispatcher } from 'svelte';

  export let open = false;
  export let title = 'Confirmer la suppression';
  export let message = 'Êtes-vous sûr de vouloir supprimer cet élément ?';
  export let confirmLabel = 'Supprimer';
  export let loading = false;

  const dispatch = createEventDispatcher();
</script>

<Modal {open} {title} size="sm" on:close={() => dispatch('cancel')}>
  <div class="flex items-start gap-3">
    <div class="flex-shrink-0 w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
      <Icon icon="heroicons:exclamation-triangle" class="h-5 w-5 text-red-600" />
    </div>
    <p class="text-sm text-gray-600 flex-1 pt-2">{message}</p>
  </div>

  <svelte:fragment slot="footer">
    <button
      on:click={() => dispatch('cancel')}
      disabled={loading}
      class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
    >
      Annuler
    </button>
    <button
      on:click={() => dispatch('confirm')}
      disabled={loading}
      class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 flex items-center gap-2"
    >
      {#if loading}
        <Icon icon="heroicons:arrow-path" class="h-4 w-4 animate-spin" />
      {/if}
      {confirmLabel}
    </button>
  </svelte:fragment>
</Modal>