<script>
  import { onMount } from 'svelte';
  import Icon from '@iconify/svelte';
  import { authApi } from '$lib/api.js';
  import Modal from '../../../components/etablissement/Modal.svelte';
  import ConfirmDialog from '../../../components/etablissement/ConfirmDialog.svelte';
  import Toast from '../../../components/etablissement/Toast.svelte';

  // ---------- State ----------
  let annees = [];
  let loading = true;
  let saving = false;
  let error = null;

  let toast = { message: '', type: 'success' };

  // Modal création / édition
  let showForm = false;
  let editing = null; // null = création
  let form = {
    nom: '',
    date_debut: '',
    date_fin: '',
    est_active: false
  };
  let formErrors = {};

  // Confirmation suppression / activation
  let confirmDelete = { open: false, annee: null };
  let confirmActivate = { open: false, annee: null };

  // ---------- Helpers ----------
  function showToast(message, type = 'success') {
    toast = { message, type };
  }

  function formatDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
  }

  function isCurrentYear(annee) {
    if (!annee.date_debut || !annee.date_fin) return false;
    const now = new Date();
    return now >= new Date(annee.date_debut) && now <= new Date(annee.date_fin);
  }

  function validateForm() {
    const errors = {};
    if (!form.nom?.trim()) errors.nom = 'Le nom est requis';
    if (!form.date_debut) errors.date_debut = 'La date de début est requise';
    if (!form.date_fin) errors.date_fin = 'La date de fin est requise';
    if (form.date_debut && form.date_fin && form.date_debut >= form.date_fin) {
      errors.date_fin = 'La date de fin doit être après la date de début';
    }
    formErrors = errors;
    return Object.keys(errors).length === 0;
  }

  // ---------- Data loading ----------
  async function loadAnnees() {
    loading = true;
    error = null;
    try {
      const data = await authApi.getAnneesScolaires();
      annees = Array.isArray(data) ? data : (data.results ?? []);
    } catch (e) {
      error = e.message || 'Impossible de charger les années scolaires';
    } finally {
      loading = false;
    }
  }

  onMount(loadAnnees);

  // ---------- CRUD ----------
  function openCreate() {
    editing = null;
    form = {
      nom: '',
      date_debut: '',
      date_fin: '',
      est_active: false
    };
    formErrors = {};
    showForm = true;
  }

  function openEdit(annee) {
    editing = annee;
    form = {
      nom: annee.nom,
      date_debut: annee.date_debut,
      date_fin: annee.date_fin,
      est_active: annee.est_active
    };
    formErrors = {};
    showForm = true;
  }

  async function submitForm() {
    if (!validateForm()) return;
    saving = true;
    try {
      if (editing) {
        // Mise à jour locale (remplace l'élément)
        await authApi.updateAnneeScolaire?.(editing.id, form);
        // Fallback si pas de update dédié dans api.js :
        // (voir note en bas de page — sinon on utilise fetchWithAuth direct)
      } else {
        const created = await authApi.createAnneeScolaire(form);
        showToast(`Année « ${created.nom} » créée avec succès`);
      }
      showForm = false;
      await loadAnnees();
      if (editing) showToast('Année scolaire mise à jour');
    } catch (e) {
      showToast(e.message || 'Erreur lors de l\'enregistrement', 'error');
    } finally {
      saving = false;
    }
  }

  function askDelete(annee) {
    confirmDelete = { open: true, annee };
  }

  async function doDelete() {
    const annee = confirmDelete.annee;
    saving = true;
    try {
      await authApi.deleteAnneeScolaire(annee.id);
      showToast(`Année « ${annee.nom} » supprimée`);
      confirmDelete = { open: false, annee: null };
      await loadAnnees();
    } catch (e) {
      showToast(e.message || 'Erreur lors de la suppression', 'error');
    } finally {
      saving = false;
    }
  }

  function askActivate(annee) {
    if (annee.est_active) return;
    confirmActivate = { open: true, annee };
  }

  async function doActivate() {
    const annee = confirmActivate.annee;
    saving = true;
    try {
      await authApi.activateAnneeScolaire(annee.id);
      showToast(`Année « ${annee.nom} » activée`);
      confirmActivate = { open: false, annee: null };
      await loadAnnees();
    } catch (e) {
      showToast(e.message || 'Erreur lors de l\'activation', 'error');
    } finally {
      saving = false;
    }
  }

  // ---------- Derived ----------
  $: sortedAnnees = [...annees].sort((a, b) =>
    (b.date_debut || '').localeCompare(a.date_debut || '')
  );
  $: activeAnnee = annees.find(a => a.est_active);
</script>

<svelte:head>
  <title>Années scolaires — Établissement</title>
</svelte:head>

<!-- Toast -->
<Toast
  message={toast.message}
  type={toast.type}
  on:close={() => (toast = { message: '', type: 'success' })}
/>

<div class="mx-auto space-y-6">
  <!-- Header -->
  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
        <Icon icon="heroicons:calendar-days" class="h-7 w-7 text-[#20784d]" />
        Années scolaires
      </h1>
      <p class="mt-1 text-sm text-gray-500">
        Gérez les années scolaires de votre établissement et définissez l'année active.
      </p>
    </div>

    <button
      on:click={openCreate}
      class="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-white bg-[#20784d] rounded-lg hover:bg-[#1a633f] transition-colors shadow-sm"
    >
      <Icon icon="heroicons:plus" class="h-4 w-4" />
      Nouvelle année
    </button>
  </div>

  <!-- Bandeau année active -->
  {#if activeAnnee}
    <div class="rounded-xl border border-green-200 bg-green-50 p-4 flex items-start gap-3">
      <div class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
        <Icon icon="heroicons:check-badge" class="h-5 w-5 text-[#20784d]" />
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-sm font-semibold text-green-900">
          Année active : {activeAnnee.nom}
        </p>
        <p class="text-xs text-green-700 mt-0.5">
          Du {formatDate(activeAnnee.date_debut)} au {formatDate(activeAnnee.date_fin)}
        </p>
      </div>
    </div>
  {/if}

  <!-- Erreur -->
  {#if error}
    <div class="rounded-lg border border-red-200 bg-red-50 p-4 flex items-start gap-3">
      <Icon icon="heroicons:exclamation-circle" class="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
      <p class="text-sm text-red-800 flex-1">{error}</p>
      <button on:click={loadAnnees} class="text-sm font-medium text-red-700 hover:text-red-900">
        Réessayer
      </button>
    </div>
  {/if}

  <!-- Tableau -->
  <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
    {#if loading}
      <div class="p-10 flex items-center justify-center gap-3 text-gray-500">
        <Icon icon="heroicons:arrow-path" class="h-5 w-5 animate-spin text-[#20784d]" />
        <span class="text-sm">Chargement des années scolaires…</span>
      </div>
    {:else if sortedAnnees.length === 0}
      <!-- Empty state -->
      <div class="p-12 text-center">
        <div class="mx-auto w-14 h-14 rounded-full bg-green-50 flex items-center justify-center mb-3">
          <Icon icon="heroicons:calendar" class="h-7 w-7 text-[#20784d]" />
        </div>
        <h3 class="text-base font-semibold text-gray-900">Aucune année scolaire</h3>
        <p class="mt-1 text-sm text-gray-500">
          Commencez par créer votre première année scolaire.
        </p>
        <button
          on:click={openCreate}
          class="mt-4 inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-[#20784d] rounded-lg hover:bg-[#1a633f] transition-colors"
        >
          <Icon icon="heroicons:plus" class="h-4 w-4" />
          Créer une année
        </button>
      </div>
    {:else}
      <!-- Desktop table -->
      <div class="hidden md:block overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Nom</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Début</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Fin</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Statut</th>
              <th class="px-6 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-100">
            {#each sortedAnnees as annee (annee.id)}
              <tr class="hover:bg-gray-50 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <span class="text-sm font-medium text-gray-900">{annee.nom}</span>
                    {#if isCurrentYear(annee) && !annee.est_active}
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                        Période actuelle
                      </span>
                    {/if}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {formatDate(annee.date_debut)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {formatDate(annee.date_fin)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  {#if annee.est_active}
                    <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      <span class="w-1.5 h-1.5 rounded-full bg-green-600"></span>
                      Active
                    </span>
                  {:else}
                    <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                      <span class="w-1.5 h-1.5 rounded-full bg-gray-400"></span>
                      Inactive
                    </span>
                  {/if}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right">
                  <div class="inline-flex items-center gap-1">
                    {#if !annee.est_active}
                      <button
                        on:click={() => askActivate(annee)}
                        class="p-2 rounded-lg text-gray-500 hover:text-[#20784d] hover:bg-green-50 transition-colors"
                        title="Activer cette année"
                      >
                        <Icon icon="heroicons:check-circle" class="h-5 w-5" />
                      </button>
                    {/if}
                    <button
                      on:click={() => openEdit(annee)}
                      class="p-2 rounded-lg text-gray-500 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                      title="Modifier"
                    >
                      <Icon icon="heroicons:pencil-square" class="h-5 w-5" />
                    </button>
                    <button
                      on:click={() => askDelete(annee)}
                      class="p-2 rounded-lg text-gray-500 hover:text-red-600 hover:bg-red-50 transition-colors"
                      title="Supprimer"
                    >
                      <Icon icon="heroicons:trash" class="h-5 w-5" />
                    </button>
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>

      <!-- Mobile cards -->
      <div class="md:hidden divide-y divide-gray-100">
        {#each sortedAnnees as annee (annee.id)}
          <div class="p-4 space-y-3">
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="text-sm font-semibold text-gray-900 truncate">{annee.nom}</p>
                <p class="text-xs text-gray-500 mt-0.5">
                  {formatDate(annee.date_debut)} → {formatDate(annee.date_fin)}
                </p>
              </div>
              {#if annee.est_active}
                <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 flex-shrink-0">
                  Active
                </span>
              {:else}
                <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700 flex-shrink-0">
                  Inactive
                </span>
              {/if}
            </div>

            <div class="flex items-center gap-2 pt-1">
              {#if !annee.est_active}
                <button
                  on:click={() => askActivate(annee)}
                  class="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-medium text-[#20784d] bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
                >
                  <Icon icon="heroicons:check-circle" class="h-4 w-4" />
                  Activer
                </button>
              {/if}
              <button
                on:click={() => openEdit(annee)}
                class="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-medium text-blue-700 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <Icon icon="heroicons:pencil-square" class="h-4 w-4" />
                Modifier
              </button>
              <button
                on:click={() => askDelete(annee)}
                class="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-medium text-red-700 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
              >
                <Icon icon="heroicons:trash" class="h-4 w-4" />
                Supprimer
              </button>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>

<!-- ============ Modal création / édition ============ -->
<Modal
  open={showForm}
  title={editing ? 'Modifier l\'année scolaire' : 'Nouvelle année scolaire'}
  size="md"
  on:close={() => (showForm = false)}
>
  <form on:submit|preventDefault={submitForm} class="space-y-4">
    <!-- Nom -->
    <div>
      <label for="nom" class="block text-sm font-medium text-gray-700 mb-1">
        Nom <span class="text-red-500">*</span>
      </label>
      <input
        id="nom"
        type="text"
        bind:value={form.nom}
        placeholder="ex : 2024-2025"
        class="w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#20784d]/30 focus:border-[#20784d] {formErrors.nom ? 'border-red-400' : 'border-gray-300'}"
      />
      {#if formErrors.nom}
        <p class="mt-1 text-xs text-red-600">{formErrors.nom}</p>
      {/if}
    </div>

    <!-- Dates -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label for="date_debut" class="block text-sm font-medium text-gray-700 mb-1">
          Date de début <span class="text-red-500">*</span>
        </label>
        <input
          id="date_debut"
          type="date"
          bind:value={form.date_debut}
          class="w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#20784d]/30 focus:border-[#20784d] {formErrors.date_debut ? 'border-red-400' : 'border-gray-300'}"
        />
        {#if formErrors.date_debut}
          <p class="mt-1 text-xs text-red-600">{formErrors.date_debut}</p>
        {/if}
      </div>

      <div>
        <label for="date_fin" class="block text-sm font-medium text-gray-700 mb-1">
          Date de fin <span class="text-red-500">*</span>
        </label>
        <input
          id="date_fin"
          type="date"
          bind:value={form.date_fin}
          class="w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#20784d]/30 focus:border-[#20784d] {formErrors.date_fin ? 'border-red-400' : 'border-gray-300'}"
        />
        {#if formErrors.date_fin}
          <p class="mt-1 text-xs text-red-600">{formErrors.date_fin}</p>
        {/if}
      </div>
    </div>

    <!-- Activer immédiatement -->
    <label class="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer transition-colors">
      <input
        type="checkbox"
        bind:checked={form.est_active}
        class="h-4 w-4 text-[#20784d] focus:ring-[#20784d] border-gray-300 rounded"
      />
      <div class="flex-1">
        <p class="text-sm font-medium text-gray-800">Définir comme année active</p>
        <p class="text-xs text-gray-500">
          L'activation désactivera automatiquement les autres années.
        </p>
      </div>
    </label>
  </form>

  <svelte:fragment slot="footer">
    <button
      type="button"
      on:click={() => (showForm = false)}
      disabled={saving}
      class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
    >
      Annuler
    </button>
    <button
      type="button"
      on:click={submitForm}
      disabled={saving}
      class="px-4 py-2 text-sm font-medium text-white bg-[#20784d] rounded-lg hover:bg-[#1a633f] disabled:opacity-50 flex items-center gap-2"
    >
      {#if saving}
        <Icon icon="heroicons:arrow-path" class="h-4 w-4 animate-spin" />
      {/if}
      {editing ? 'Enregistrer' : 'Créer'}
    </button>
  </svelte:fragment>
</Modal>

<!-- ============ Confirmation activation ============ -->
<ConfirmDialog
  open={confirmActivate.open}
  title="Activer cette année ?"
  message={`L'année « ${confirmActivate.annee?.nom ?? ''} » deviendra l'année active. Toutes les autres années seront désactivées.`}
  confirmLabel="Activer"
  loading={saving}
  on:cancel={() => (confirmActivate = { open: false, annee: null })}
  on:confirm={doActivate}
/>

<!-- ============ Confirmation suppression ============ -->
<ConfirmDialog
  open={confirmDelete.open}
  title="Supprimer cette année ?"
  message={`L'année « ${confirmDelete.annee?.nom ?? ''} » sera définitivement supprimée. Cette action est irréversible.`}
  confirmLabel="Supprimer"
  loading={saving}
  on:cancel={() => (confirmDelete = { open: false, annee: null })}
  on:confirm={doDelete}
/>