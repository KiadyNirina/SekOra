<!-- src/lib/components/register/ProfesseurForm.svelte -->
<script>
  import Icon from '@iconify/svelte';
  import { createEventDispatcher } from 'svelte';
  import { authApi } from '$lib/api';
  import { getProfesseurFormData } from '$lib/formData';

  const dispatch = createEventDispatcher();

  let isLoading = false;
  let errorMessage = '';

  let professeurData = {
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    matiere: '',
    etablissement: '',
    password: '',
    confirmPassword: ''
  };

  async function handleSubmit() {
    isLoading = true;
    errorMessage = '';

    try {
      if (professeurData.password !== professeurData.confirmPassword) {
        throw new Error('Les mots de passe ne correspondent pas');
      }
      const formData = getProfesseurFormData(professeurData);
      await authApi.registerProfesseur(formData);
      dispatch('success');
    } catch (error) {
      errorMessage = error.message || "Une erreur s'est produite lors de l'inscription";
    } finally {
      isLoading = false;
    }
  }
</script>

{#if errorMessage}
  <div class="mb-4 bg-red-50 border-l-4 border-red-400 p-4">
    <div class="flex">
      <div class="flex-shrink-0">
        <Icon icon="heroicons:exclamation-circle" class="h-5 w-5 text-red-400" />
      </div>
      <div class="ml-3">
        <p class="text-sm text-red-700">{errorMessage}</p>
      </div>
    </div>
  </div>
{/if}

<form class="space-y-6" on:submit|preventDefault={handleSubmit}>
  <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
    <div>
      <label for="prof-nom" class="block text-sm font-medium text-gray-700">Nom</label>
      <input
        id="prof-nom"
        type="text"
        bind:value={professeurData.nom}
        required
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
      />
    </div>

    <div>
      <label for="prof-prenom" class="block text-sm font-medium text-gray-700">Prénom</label>
      <input
        id="prof-prenom"
        type="text"
        bind:value={professeurData.prenom}
        required
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
      />
    </div>

    <div>
      <label for="prof-email" class="block text-sm font-medium text-gray-700">Email</label>
      <input
        id="prof-email"
        type="email"
        bind:value={professeurData.email}
        required
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
      />
    </div>

    <div>
      <label for="prof-telephone" class="block text-sm font-medium text-gray-700">Téléphone</label>
      <input
        id="prof-telephone"
        type="tel"
        bind:value={professeurData.telephone}
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
      />
    </div>

    <div>
      <label for="prof-matiere" class="block text-sm font-medium text-gray-700">Matière enseignée</label>
      <input
        id="prof-matiere"
        type="text"
        bind:value={professeurData.matiere}
        required
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
      />
    </div>

    <div>
      <label for="prof-etablissement" class="block text-sm font-medium text-gray-700">Établissement</label>
      <input
        id="prof-etablissement"
        type="text"
        bind:value={professeurData.etablissement}
        required
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
      />
    </div>

    <div>
      <label for="prof-password" class="block text-sm font-medium text-gray-700">Mot de passe</label>
      <input
        id="prof-password"
        type="password"
        bind:value={professeurData.password}
        required
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
      />
    </div>

    <div>
      <label for="prof-confirm-password" class="block text-sm font-medium text-gray-700">Confirmer le mot de passe</label>
      <input
        id="prof-confirm-password"
        type="password"
        bind:value={professeurData.confirmPassword}
        required
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
      />
    </div>
  </div>

  <div>
    <button
      type="submit"
      disabled={isLoading}
      class={`w-full flex justify-center py-2 px-4 border border-transparent rounded-full text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
    >
      {#if isLoading}
        <Icon icon="heroicons:arrow-path" class="animate-spin h-5 w-5 mr-2" />
        Inscription en cours...
      {:else}
        S'inscrire en tant que professeur
      {/if}
    </button>
  </div>
</form>