<script>
  import Icon from '@iconify/svelte';
  import { fade } from 'svelte/transition';
  import { authApi, authStore } from '$lib/api';
  
  let activeTab = 'etablissement';
  let email = '';
  let password = '';
  let rememberMe = false;
  let isLoading = false;
  let errorMessage = '';
  let showPassword = false;
  
  const userTypes = [
    { id: 'etablissement', label: 'Établissement', icon: 'heroicons:building-office-2' },
    { id: 'professeur', label: 'Professeur', icon: 'heroicons:academic-cap' },
    { id: 'eleve', label: 'Élève', icon: 'heroicons:user' },
    { id: 'parent', label: 'Parent', icon: 'heroicons:users' }
  ];
  
  async function handleLogin() {
    if (!email || !password) {
      errorMessage = 'Veuillez remplir tous les champs';
      return;
    }
    
    isLoading = true;
    errorMessage = '';

    try {
      const { access, refresh, user_type } = await authApi.login(email, password);

      if (user_type !== activeTab) {
        throw new Error(
          `Ce compte est un compte ${user_type}, pas un compte ${activeTab}.`
        );
      }
      
      authStore.setTokens({ access, refresh });

      await authApi.getProfile();
      
      if (rememberMe) {
        document.cookie = `refresh_token=${refresh}; path=/; max-age=${7 * 24 * 60 * 60}`;
      }

      switch (user_type) {
        case 'etablissement':
          window.location.href = '/etablissement/dashboard';
          break;
        case 'professeur':
          window.location.href = '/professeur/dashboard';
          break;
        case 'eleve':
          window.location.href = '/eleve/dashboard';
          break;
        case 'parent':
          window.location.href = '/parent/dashboard';
          break;
      }
    } catch (err) {
      if (err?.response?.data) {
        const data = err.response.data;

        if (data.non_field_errors) {
          errorMessage = Array.isArray(data.non_field_errors)
            ? data.non_field_errors[0]
            : data.non_field_errors;
        } else if (data.detail) {
          errorMessage = data.detail;
        } else {
          errorMessage = 'Erreur de connexion';
        }
      } else {
        errorMessage = err?.message || 'Erreur de connexion';
      }

      authStore.clearTokens();
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
  <div class="sm:mx-auto sm:w-full sm:max-w-md">
    <a href="/" class="flex justify-center h-12 mx-auto">
      <img src="/icons/favicon.png" class="h-12" alt="Logo">
    </a>
    <h2 class="mt-6 text-center text-3xl font-medium text-gray-900">
      Connectez-vous à votre compte
    </h2>
    <p class="mt-2 text-center text-sm text-gray-600">
      Sélectionnez votre profil pour continuer
    </p>
  </div>

  <div class="mt-8 mx-auto w-full max-w-md">
    <div class="bg-white py-8 px-4 border border-gray-200 rounded-[10%] px-10">
      <!-- Sélecteur de type d'utilisateur -->
      <div class="mb-6">
        <div class="flex space-x-0 overflow-x-auto pb-2">
          {#each userTypes as type}
            <button
              on:click={() => activeTab = type.id}
              class={`px-4 py-2 rounded-full flex items-center space-x-2 whitespace-nowrap ${activeTab === type.id ? 'bg-green-100 text-[#20784d]' : 'text-gray-600 hover:bg-gray-100'}`}
            >
              <Icon icon={type.icon} class="h-5 w-5" />
              <span>{type.label}</span>
            </button>
          {/each}
        </div>
      </div>
      
      <!-- Formulaire de connexion -->
      {#if errorMessage}
        <div transition:fade class="mb-4 bg-red-50 border-l-4 border-red-400 p-4">
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
      
      <form class="space-y-6" on:submit|preventDefault={handleLogin}>
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">
            Adresse email
          </label>
          <div class="mt-1">
            <input
              id="email"
              name="email"
              type="email"
              autocomplete="email"
              bind:value={email}
              required
              class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-full placeholder-gray-400 focus:outline-none focus:ring-[#20784d] focus:border-[#20784d] sm:text-sm"
            />
          </div>
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-gray-700">
            Mot de passe
          </label>
          <div class="mt-1 relative">
            <input
              id="password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              autocomplete="current-password"
              bind:value={password}
              required
              class="appearance-none block w-full pl-3 pr-10 py-2 border border-gray-300 rounded-full placeholder-gray-400 focus:outline-none focus:ring-[#20784d] focus:border-[#20784d] sm:text-sm"
            />
            <button
              type="button"
              on:click={() => showPassword = !showPassword}
              class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-[#20784d] focus:outline-none"
              aria-label={showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
            >
              <Icon
                icon={showPassword ? 'heroicons:eye-slash' : 'heroicons:eye'}
                class="h-5 w-5"
              />
            </button>
          </div>
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <input
              id="remember-me"
              name="remember-me"
              type="checkbox"
              bind:checked={rememberMe}
              class="h-4 w-4 text-[#20784d] focus:ring-[#20784d] border-gray-300 rounded"
            />
            <label for="remember-me" class="ml-2 block text-sm text-gray-900">
              Se souvenir de moi
            </label>
          </div>

          <div class="text-sm">
            <a href="/forgot-password" class="font-medium text-[#20784d] hover:text-[#20784d]">
              Mot de passe oublié ?
            </a>
          </div>
        </div>

        <div>
          <button
            type="submit"
            disabled={isLoading}
            class={`w-full flex justify-center py-2 px-4 border border-transparent rounded-full text-sm font-medium text-white bg-[#20784d] hover:bg-[#20784d] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#20784d] ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
          >
            {#if isLoading}
              <Icon icon="heroicons:arrow-path" class="animate-spin h-5 w-5 mr-2" />
              Connexion en cours...
            {:else}
              Se connecter
            {/if}
          </button>
        </div>
      </form>

      <div class="mt-6">
        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-300"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-white text-gray-500">
              Pas encore de compte ?
            </span>
          </div>
        </div>

        <div class="mt-6">
          <a
            href="/signup"
            class="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-full text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#20784d]"
          >
            S'inscrire
          </a>
        </div>
      </div>
    </div>
  </div>
</div>