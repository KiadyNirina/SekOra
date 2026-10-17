<!-- src/lib/components/register/EleveForm.svelte -->
<script>
  import Icon from '@iconify/svelte';
  import { createEventDispatcher } from 'svelte';
  import { authApi } from '$lib/api';
  import { getEleveFormData } from '$lib/formData';

  const dispatch = createEventDispatcher();

  let isLoading = false;
  let errorMessage = '';

  let eleveData = {
    nom: '',
    prenom: '',
    email: '',
    classe: '',
    etablissement: '',
    password: '',
    confirmPassword: ''
  };

  async function handleSubmit() {
    isLoading = true;
    errorMessage = '';

    try {
      if (eleveData.password !== eleveData.confirmPassword) {
        throw new Error('Les mots de passe ne correspondent pas');
      }
      const formData = getEleveFormData(eleveData);
      await authApi.registerEleve(formData);
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
      <label for="eleve-nom" class="block text-sm font-medium text-gray-700">Nom</label>
      <input
        id="eleve-nom"
        type="text"
        bind:value={eleveData.nom}
        required
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
      />
    </div>

    <div>
      <label for="eleve-prenom" class="block text-sm font-medium text-gray-700">Prénom</label>
      <input
        id="eleve-prenom"
        type="text"
        bind:value={eleveData.prenom}
        required
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
      />
    </div>

    <div>
      <label for="eleve-email" class="block text-sm font-medium text-gray-700">Email</label>
      <input
        id="eleve-email"
        type="email"
        bind:value={eleveData.email}
        required
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
      />
    </div>

    <div>
      <label for="eleve-classe" class="block text-sm font-medium text-gray-700">Classe</label>
      <input
        id="eleve-classe"
        type="text"
        bind:value={eleveData.classe}
        required
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
      />
    </div>

    <div class="sm:col-span-2">
      <label for="eleve-etablissement" class="block text-sm font-medium text-gray-700">Établissement</label>
      <input
        id="eleve-etablissement"
        type="text"
        bind:value={eleveData.etablissement}
        required
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
      />
    </div>

    <div>
      <label for="eleve-password" class="block text-sm font-medium text-gray-700">Mot de passe</label>
      <input
        id="eleve-password"
        type="password"
        bind:value={eleveData.password}
        required
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
      />
    </div>

    <div>
      <label for="eleve-confirm-password" class="block text-sm font-medium text-gray-700">Confirmer le mot de passe</label>
      <input
        id="eleve-confirm-password"
        type="password"
        bind:value={eleveData.confirmPassword}
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
        S'inscrire en tant qu'élève
      {/if}
    </button>
  </div>
</form>