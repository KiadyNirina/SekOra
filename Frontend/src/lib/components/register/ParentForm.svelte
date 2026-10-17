<!-- src/lib/components/register/ParentForm.svelte -->
<script>
  import Icon from '@iconify/svelte';
  import { createEventDispatcher } from 'svelte';
  import { authApi } from '$lib/api';
  import { getParentFormData } from '$lib/formData';

  const dispatch = createEventDispatcher();

  let isLoading = false;
  let errorMessage = '';

  let parentData = {
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    enfants: [],
    password: '',
    confirmPassword: ''
  };

  $: enfantsText = parentData.enfants.join(', ');

  function updateEnfants(input) {
    parentData.enfants = input
      ? input.split(',').map((item) => item.trim()).filter((item) => item !== '')
      : [];
  }

  async function handleSubmit() {
    isLoading = true;
    errorMessage = '';

    try {
      if (parentData.password !== parentData.confirmPassword) {
        throw new Error('Les mots de passe ne correspondent pas');
      }
      const formData = getParentFormData(parentData);
      await authApi.registerParent(formData);
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
      <label for="parent-nom" class="block text-sm font-medium text-gray-700">Nom</label>
      <input
        id="parent-nom"
        type="text"
        bind:value={parentData.nom}
        required
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
      />
    </div>

    <div>
      <label for="parent-prenom" class="block text-sm font-medium text-gray-700">Prénom</label>
      <input
        id="parent-prenom"
        type="text"
        bind:value={parentData.prenom}
        required
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
      />
    </div>

    <div>
      <label for="parent-email" class="block text-sm font-medium text-gray-700">Email</label>
      <input
        id="parent-email"
        type="email"
        bind:value={parentData.email}
        required
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
      />
    </div>

    <div>
      <label for="parent-telephone" class="block text-sm font-medium text-gray-700">Téléphone</label>
      <input
        id="parent-telephone"
        type="tel"
        bind:value={parentData.telephone}
        required
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
      />
    </div>

    <div class="sm:col-span-2">
      <label for="parent-enfants" class="block text-sm font-medium text-gray-700">Enfants (noms et classes, séparés par des virgules)</label>
      <textarea
        id="parent-enfants"
        bind:value={enfantsText}
        on:input={(e) => updateEnfants(e.target.value)}
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
        placeholder="Ex: Jean Dupont (3ème A), Marie Dupont (5ème B)"
      ></textarea>
    </div>

    <div>
      <label for="parent-password" class="block text-sm font-medium text-gray-700">Mot de passe</label>
      <input
        id="parent-password"
        type="password"
        bind:value={parentData.password}
        required
        class="mt-1 block w-full border border-gray-300 rounded-full py-2 px-3 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
      />
    </div>

    <div>
      <label for="parent-confirm-password" class="block text-sm font-medium text-gray-700">Confirmer le mot de passe</label>
      <input
        id="parent-confirm-password"
        type="password"
        bind:value={parentData.confirmPassword}
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
        S'inscrire en tant que parent
      {/if}
    </button>
  </div>
</form>