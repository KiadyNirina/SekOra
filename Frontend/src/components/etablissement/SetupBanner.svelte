<script>
  import Icon from '@iconify/svelte';
  import { onMount } from 'svelte';
  import { anneeActive, loadAnneesScolaires } from '$lib/stores/anneeScolaire.js';

  onMount(loadAnneesScolaires);
</script>

{#if $anneeActive === null}
  <div class="bg-amber-50 border-b border-amber-200 px-6 py-3">
    <div class="flex flex-col sm:flex-row sm:items-center gap-3 max-w-7xl mx-auto">
      <Icon icon="heroicons:exclamation-triangle" class="h-5 w-5 text-amber-600 flex-shrink-0" />
      <p class="text-sm text-amber-800 flex-1">
        <strong class="font-semibold">Aucune année scolaire active.</strong>
        Créez une année scolaire pour commencer à gérer vos élèves, classes et cours.
      </p>
      <a
        href="/etablissement/annees-scolaires"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-amber-600 rounded-lg hover:bg-amber-700 transition-colors flex-shrink-0"
      >
        <Icon icon="heroicons:plus" class="h-3.5 w-3.5" />
        Créer une année
      </a>
    </div>
  </div>
{/if}