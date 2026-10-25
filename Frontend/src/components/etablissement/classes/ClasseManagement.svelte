<script>
  import { onMount } from 'svelte';
  import Icon from '@iconify/svelte';
  import { authApi } from '$lib/api';
  import { anneeActive, loadAnneesScolaires } from '$lib/stores/anneeScolaire.js';

  let classes = [];
  let loading = true;
  let error = null;
  let successMessage = null;
  let showForm = false;

  // Options pour les selects
  let etablissementId = null;
  let anneesOptions = [];
  let professeursOptions = [];
  let matieresOptions = [];   // ← NOUVEAU

  // Formulaire
  let isEditing = false;
  let currentClasseId = null;
  let newClasse = {
    nom: '',
    niveau: '',
    section: '',
    etablissement: null,
    annee_scolaire: '',
    professeur_principal: '',
    matieres: []              // ← NOUVEAU
  };

  // Filtres
  let searchTerm = '';
  let filterAnnee = '';
  let filterMatiere = '';     // ← NOUVEAU (optionnel)
  let filteredClasses = [];

  onMount(async () => {
    await loadAnneesScolaires();
    await loadData();
  });

  async function loadData() {
    loading = true;
    error = null;
    try {
      const profile = await authApi.getProfile();
      etablissementId = profile.profile?.id || profile.etablissement?.id;

      if (!etablissementId) {
        throw new Error('Établissement non trouvé');
      }

      // Charger les données en parallèle
      const [classesData, anneesData, professeursData] = await Promise.all([
        authApi.getClasses({ etablissement: etablissementId }),
        authApi.getAnneesScolaires(),
        authApi.getProfesseurs({ etablissement: etablissementId })
      ]);

      classes = classesData.results || classesData;

      anneesOptions = (anneesData || []).map(a => ({
        value: a.id,
        label: a.nom,
        est_active: a.est_active
      }));

      professeursOptions = (professeursData.results || professeursData || []).map(p => ({
        value: p.id,
        label: p.user?.first_name + ' ' + p.user?.last_name || 'Professeur'
      }));

      // Pré-sélectionner l'année active
      const activeAnnee = anneesOptions.find(a => a.est_active);
      if (activeAnnee && !newClasse.annee_scolaire) {
        newClasse.annee_scolaire = activeAnnee.value;
        await loadMatieresForAnnee(activeAnnee.value);
      }

      applyFilters();
    } catch (err) {
      error = err.message || 'Erreur lors du chargement des données';
      console.error('Erreur:', err);
    } finally {
      loading = false;
    }
  }

  // ⬇️ NOUVEAU — Charge les matières de l'année sélectionnée
  async function loadMatieresForAnnee(anneeId) {
    if (!anneeId) {
      matieresOptions = [];
      return;
    }
    try {
      const data = await authApi.getMatieres({
        etablissement: etablissementId,
        annee_scolaire: anneeId,
      });
      matieresOptions = (data.results || data || []).map(m => ({
        value: m.id,
        label: m.nom,
        description: m.description,
      }));
    } catch (err) {
      console.error('Erreur chargement matières:', err);
      matieresOptions = [];
    }
  }

  // ⬇️ NOUVEAU — Quand on change l'année dans le formulaire
  async function handleAnneeChange() {
    // Filtre les matières déjà sélectionnées à celles de la nouvelle année
    const validIds = new Set(matieresOptions.map(m => m.value));
    newClasse.matieres = newClasse.matieres.filter(id => validIds.has(id));
    await loadMatieresForAnnee(newClasse.annee_scolaire);
  }

  // ⬇️ NOUVEAU — Toggle sélection matière
  function toggleMatiere(matiereId) {
    if (newClasse.matieres.includes(matiereId)) {
      newClasse.matieres = newClasse.matieres.filter(id => id !== matiereId);
    } else {
      newClasse.matieres = [...newClasse.matieres, matiereId];
    }
  }

  function applyFilters() {
    let result = [...classes];

    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      result = result.filter(c =>
        c.nom?.toLowerCase().includes(search) ||
        c.niveau?.toLowerCase().includes(search) ||
        c.section?.toLowerCase().includes(search)
      );
    }

    if (filterAnnee) {
      const filterVal = parseInt(filterAnnee);
      result = result.filter(c => {
        const anneeId = c.annee_scolaire?.id || parseInt(c.annee_scolaire);
        return anneeId === filterVal;
      });
    }

    // ⬇️ NOUVEAU — filtre matière
    if (filterMatiere) {
      const matId = parseInt(filterMatiere);
      result = result.filter(c => (c.matieres || []).includes(matId));
    }

    filteredClasses = result;
  }

  function resetForm() {
    isEditing = false;
    currentClasseId = null;
    showForm = false;
    const activeAnnee = anneesOptions.find(a => a.est_active);
    newClasse = {
      nom: '',
      niveau: '',
      section: '',
      etablissement: etablissementId,
      annee_scolaire: activeAnnee?.value || '',
      professeur_principal: '',
      matieres: []
    };
    loadMatieresForAnnee(activeAnnee?.value);
  }

  function openAddForm() {
    resetForm();
    showForm = true;
  }

  async function editClasse(classe) {
    isEditing = true;
    currentClasseId = classe.id;
    showForm = true;

    const anneeId = classe.annee_scolaire?.id || classe.annee_scolaire || '';

    newClasse = {
      nom: classe.nom,
      niveau: classe.niveau,
      section: classe.section || '',
      etablissement: classe.etablissement,
      annee_scolaire: anneeId,
      professeur_principal: classe.professeur_principal || '',
      matieres: classe.matieres || []    // ← NOUVEAU
    };

    // Charge les matières de l'année de la classe
    await loadMatieresForAnnee(anneeId);
  }

  async function saveClasse() {
    if (!newClasse.nom || !newClasse.niveau || !newClasse.annee_scolaire) {
      error = 'Le nom, le niveau et l\'année scolaire sont obligatoires';
      setTimeout(() => error = null, 3000);
      return;
    }

    loading = true;
    error = null;

    try {
      const classeData = {
        nom: newClasse.nom,
        niveau: newClasse.niveau,
        section: newClasse.section || null,
        etablissement: etablissementId,
        annee_scolaire_id: parseInt(newClasse.annee_scolaire),
        professeur_principal: newClasse.professeur_principal ? parseInt(newClasse.professeur_principal) : null,
        matieres: newClasse.matieres,    // ← NOUVEAU
      };

      if (isEditing && currentClasseId) {
        await authApi.updateClasse(currentClasseId, classeData);
        successMessage = 'Classe modifiée avec succès !';
      } else {
        await authApi.createClasse(classeData);
        successMessage = 'Classe ajoutée avec succès !';
      }

      setTimeout(() => successMessage = null, 3000);
      resetForm();
      await loadData();
    } catch (err) {
      error = err.message || 'Erreur lors de la sauvegarde';
      console.error('Erreur:', err);
      setTimeout(() => error = null, 3000);
    } finally {
      loading = false;
    }
  }

  async function deleteClasse(id) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette classe ?')) return;

    loading = true;
    error = null;

    try {
      await authApi.deleteClasse(id);
      successMessage = 'Classe supprimée avec succès !';
      setTimeout(() => successMessage = null, 3000);
      await loadData();
    } catch (err) {
      error = err.message || 'Erreur lors de la suppression';
      console.error('Erreur:', err);
      setTimeout(() => error = null, 3000);
    } finally {
      loading = false;
    }
  }

  function getAnneeLabel(classe) {
    if (classe.annee_scolaire && typeof classe.annee_scolaire === 'object') {
      return classe.annee_scolaire.nom || 'N/A';
    }
    if (classe.annee_scolaire) {
      const idNum = parseInt(classe.annee_scolaire);
      const found = anneesOptions.find(a => parseInt(a.value) === idNum);
      return found ? found.label : 'N/A';
    }
    return 'N/A';
  }

  function getProfesseurLabel(id) {
    const found = professeursOptions.find(p => p.value === parseInt(id));
    return found ? found.label : 'Non assigné';
  }

  // ⬇️ NOUVEAU — Récupère les noms des matières d'une classe
  function getMatieresLabels(classe) {
    const ids = classe.matieres || [];
    return ids
      .map(id => matieresOptions.find(m => m.value === id)?.label)
      .filter(Boolean);
  }

  $: applyFilters();
</script>

<div>
  <!-- En-tête -->
  <div class="sm:flex sm:items-center justify-between">
    <div class="mb-4 sm:mb-0">
      <h1 class="text-2xl font-bold text-gray-900">Gestion des Classes</h1>
      <p class="mt-2 text-sm text-gray-700">
        {classes.length} classe{classes.length > 1 ? 's' : ''} au total
        {#if $anneeActive}
          <span class="ml-2 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <Icon icon="heroicons:calendar" class="h-3 w-3" />
            {$anneeActive.nom}
          </span>
        {/if}
      </p>
    </div>
    <div class="flex space-x-3">
      <button
        on:click={openAddForm}
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
      >
        <Icon icon="heroicons:plus-sm" class="-ml-1 mr-2 h-5 w-5" />
        Nouvelle classe
      </button>
    </div>
  </div>

  <!-- Messages -->
  {#if successMessage}
    <div class="m-4 p-4 bg-green-50 border border-green-200 rounded-md">
      <div class="flex items-center">
        <Icon icon="heroicons:check-circle" class="h-5 w-5 text-green-400 mr-2" />
        <p class="text-sm text-green-700">{successMessage}</p>
      </div>
    </div>
  {/if}

  {#if error}
    <div class="m-4 p-4 bg-red-50 border border-red-200 rounded-md">
      <div class="flex items-center">
        <Icon icon="heroicons:x-circle" class="h-5 w-5 text-red-400 mr-2" />
        <p class="text-sm text-red-700">{error}</p>
      </div>
    </div>
  {/if}

  <!-- Formulaire -->
  {#if showForm}
    <div class="mt-6 mb-6 p-4 border border-gray-200 rounded-lg bg-gray-50">
      <h4 class="text-sm font-medium text-gray-700 mb-4">
        {isEditing ? 'Modifier la classe' : 'Ajouter une nouvelle classe'}
      </h4>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <label for="classe-nom" class="block text-xs font-medium text-gray-700">
            Nom <span class="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="classe-nom"
            bind:value={newClasse.nom}
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
            placeholder="Ex: 3ème A"
          />
        </div>

        <div>
          <label for="classe-niveau" class="block text-xs font-medium text-gray-700">
            Niveau <span class="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="classe-niveau"
            bind:value={newClasse.niveau}
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
            placeholder="Ex: 3ème, Terminale"
          />
        </div>

        <div>
          <label for="classe-section" class="block text-xs font-medium text-gray-700">
            Section
          </label>
          <input
            type="text"
            id="classe-section"
            bind:value={newClasse.section}
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-1.5 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
            placeholder="Ex: A, B, S, ES"
          />
        </div>

        <div>
          <label for="classe-annee" class="block text-xs font-medium text-gray-700">
            Année scolaire <span class="text-red-500">*</span>
          </label>
          <select
            id="classe-annee"
            bind:value={newClasse.annee_scolaire}
            on:change={handleAnneeChange}
            class="mt-1 block w-full pl-3 pr-10 py-1.5 text-sm border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 rounded-md"
          >
            <option value="">Sélectionner</option>
            {#each anneesOptions as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
        </div>

        <div>
          <label for="classe-professeur" class="block text-xs font-medium text-gray-700">
            Professeur principal
          </label>
          <select
            id="classe-professeur"
            bind:value={newClasse.professeur_principal}
            class="mt-1 block w-full pl-3 pr-10 py-1.5 text-sm border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 rounded-md"
          >
            <option value="">Non assigné</option>
            {#each professeursOptions as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
        </div>

        <!-- ⬇️ NOUVEAU — Sélecteur de matières -->
        <div class="lg:col-span-4">
          <label class="block text-xs font-medium text-gray-700 mb-2">
            Matières enseignées
            {#if newClasse.matieres.length > 0}
              <span class="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                {newClasse.matieres.length} sélectionnée{newClasse.matieres.length > 1 ? 's' : ''}
              </span>
            {/if}
          </label>

          {#if !newClasse.annee_scolaire}
            <p class="text-sm text-gray-500 italic">Sélectionnez d'abord une année scolaire.</p>
          {:else if matieresOptions.length === 0}
            <p class="text-sm text-gray-500 italic">
              Aucune matière disponible pour cette année.
              <a href="/etablissement/matieres" class="text-green-600 hover:underline">
                Créer des matières →
              </a>
            </p>
          {:else}
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
              {#each matieresOptions as matiere (matiere.value)}
                <label
                  class="flex items-center gap-2 p-2 rounded-lg border cursor-pointer transition-colors
                  {newClasse.matieres.includes(matiere.value)
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 bg-white hover:bg-gray-50'}"
                >
                  <input
                    type="checkbox"
                    checked={newClasse.matieres.includes(matiere.value)}
                    on:change={() => toggleMatiere(matiere.value)}
                    class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                  />
                  <span class="text-sm text-gray-800 truncate">{matiere.label}</span>
                </label>
              {/each}
            </div>
          {/if}
        </div>

        <div class="lg:col-span-4 flex items-end space-x-2">
          <button
            on:click={saveClasse}
            disabled={loading}
            class="inline-flex items-center px-4 py-1.5 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {#if loading}
              <Icon icon="heroicons:arrow-path" class="h-4 w-4 animate-spin mr-1" />
            {/if}
            {isEditing ? 'Modifier' : 'Ajouter'}
          </button>

          <button
            on:click={resetForm}
            class="inline-flex items-center px-4 py-1.5 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            Annuler
          </button>
        </div>
      </div>
    </div>
  {/if}

  <!-- Filtres et recherche -->
  <div class="mt-6 bg-white shadow-sm rounded-lg p-6 border border-gray-200">
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div>
        <label for="filter-annee" class="block text-xs font-medium text-gray-700">Année scolaire</label>
        <select
          id="filter-annee"
          bind:value={filterAnnee}
          on:change={applyFilters}
          class="mt-1 block w-full pl-3 pr-10 py-1.5 text-sm border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 rounded-md"
        >
          <option value="">Toutes</option>
          {#each anneesOptions as option}
            <option value={option.value}>{option.label}</option>
          {/each}
        </select>
      </div>

      <div>
        <label for="filter-matiere" class="block text-xs font-medium text-gray-700">Matière</label>
        <select
          id="filter-matiere"
          bind:value={filterMatiere}
          on:change={applyFilters}
          class="mt-1 block w-full pl-3 pr-10 py-1.5 text-sm border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 rounded-md"
        >
          <option value="">Toutes</option>
          {#each matieresOptions as option}
            <option value={option.value}>{option.label}</option>
          {/each}
        </select>
      </div>

      <div class="sm:col-span-2 lg:col-span-2">
        <label for="search-classes" class="block text-xs font-medium text-gray-700">Recherche</label>
        <div class="relative mt-1">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Icon icon="heroicons:magnifying-glass" class="h-4 w-4 text-gray-400" />
          </div>
          <input
            type="text"
            id="search-classes"
            bind:value={searchTerm}
            on:input={applyFilters}
            class="block w-full pl-9 pr-3 py-1.5 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-green-500 focus:border-green-500 sm:text-sm"
            placeholder="Rechercher une classe..."
          />
        </div>
      </div>
    </div>
  </div>

  <!-- Liste des classes -->
  <div class="mt-6 shadow-sm border border-gray-200 rounded-lg overflow-hidden">
  {#if loading && classes.length === 0}
    <div class="flex justify-center items-center py-12">
      <Icon icon="heroicons:arrow-path" class="h-8 w-8 animate-spin text-green-600" />
      <span class="ml-2 text-gray-600">Chargement...</span>
    </div>
  {:else if filteredClasses.length === 0}
    <div class="text-center py-12">
      <Icon icon="heroicons:academic-cap" class="h-12 w-12 text-gray-400 mx-auto mb-4" />
      <p class="text-gray-500 text-sm">
        {searchTerm || filterAnnee || filterMatiere ? 'Aucune classe ne correspond à votre recherche' : 'Aucune classe trouvée'}
      </p>
      {#if !searchTerm && !filterAnnee && !filterMatiere}
        <button
          on:click={openAddForm}
          class="mt-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-green-700 bg-green-100 hover:bg-green-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        >
          <Icon icon="heroicons:plus-sm" class="-ml-1 mr-2 h-5 w-5" />
          Ajouter une classe
        </button>
      {/if}
    </div>
  {:else}
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Classe
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Niveau
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Section
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Année
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Matières
            </th>
            <th scope="col" class="relative px-6 py-3">
              <span class="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          {#each filteredClasses as classe}
            <tr class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10 bg-indigo-100 rounded-full flex items-center justify-center">
                    <Icon icon="heroicons:academic-cap" class="h-5 w-5 text-indigo-600" />
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">{classe.nom}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{classe.niveau}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{classe.section || '-'}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                  {getAnneeLabel(classe)}
                </span>
              </td>

              <!-- ⬇️ NOUVEAU — Colonne Matières -->
              <td class="px-6 py-4">
                {#if (classe.matieres || []).length > 0}
                  <div class="flex flex-wrap gap-1 max-w-xs">
                    {#each getMatieresLabels(classe).slice(0, 3) as label}
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-50 text-purple-700">
                        {label}
                      </span>
                    {/each}
                    {#if classe.matieres.length > 3}
                      <span
                        class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600 cursor-help"
                        title={getMatieresLabels(classe).slice(3).join(', ')}
                      >
                        +{classe.matieres.length - 3}
                      </span>
                    {/if}
                  </div>
                {:else}
                  <span class="text-xs text-gray-400 italic">Aucune</span>
                {/if}
              </td>

              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end space-x-3">
                  <button
                    on:click={() => editClasse(classe)}
                    class="text-green-600 hover:text-green-900"
                  >
                    <Icon icon="heroicons:pencil-square" class="h-5 w-5" />
                  </button>
                  <button
                    on:click={() => deleteClasse(classe.id)}
                    class="text-red-600 hover:text-red-900"
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

    <!-- Statistiques -->
    <div class="bg-gray-50 px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
      <div class="text-sm text-gray-700">
        Affichage de <span class="font-medium">{filteredClasses.length}</span> classe{filteredClasses.length > 1 ? 's' : ''}
        {#if classes.length > filteredClasses.length}
          sur <span class="font-medium">{classes.length}</span> au total
        {/if}
      </div>
      <button
        on:click={loadData}
        disabled={loading}
        class="inline-flex items-center px-3 py-1 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
      >
        <Icon icon="heroicons:arrow-path" class={`h-4 w-4 mr-1 ${loading ? 'animate-spin' : ''}`} />
        Rafraîchir
      </button>
    </div>
  {/if}
  </div>
</div>

<style>
  .animate-spin {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style>