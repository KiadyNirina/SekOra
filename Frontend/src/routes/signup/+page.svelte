<!-- src/routes/register/+page.svelte -->
<script>
  import Icon from '@iconify/svelte';
  import UserTypeSelector from '$lib/components/register/UserTypeSelector.svelte';
  import EtablissementForm from '$lib/components/register/EtablissementForm.svelte';
  import ProfesseurForm from '$lib/components/register/ProfesseurForm.svelte';
  import EleveForm from '$lib/components/register/EleveForm.svelte';
  import ParentForm from '$lib/components/register/ParentForm.svelte';

  const userTypes = [
    { id: 'etablissement', label: 'Établissement', icon: 'heroicons:building-office-2', description: 'Créez et gérez votre établissement scolaire', available: true },
    { id: 'professeur', label: 'Professeur', icon: 'heroicons:academic-cap', description: 'Enseignez et gérez vos classes', available: false },
    { id: 'eleve', label: 'Élève', icon: 'heroicons:user', description: 'Accédez à vos cours et devoirs', available: false },
    { id: 'parent', label: 'Parent', icon: 'heroicons:users', description: 'Suivez la scolarité de vos enfants', available: false }
  ];

  let selectedType = null;
  let activeTab = 'etablissement';
  let showForm = false;

  function selectType(typeId) {
    selectedType = typeId;
  }

  function goToForm() {
    if (selectedType) {
      activeTab = selectedType;
      showForm = true;
    }
  }

  function goBack() {
    showForm = false;
    selectedType = null;
  }

  function handleSuccess() {
    window.location.href = '/etablissement/dashboard';
  }
</script>

<div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
  <div class="sm:mx-auto sm:w-full sm:max-w-md">
    <a href="/" class="flex justify-center h-12 mx-auto">
      <img src="/icons/favicon.png" class="h-12" alt="Logo">
    </a>
    <h2 class="mt-6 text-center text-3xl font-medium text-gray-900">
      Créez votre compte
    </h2>
    <p class="mt-2 text-center text-sm text-gray-600">
      {showForm ? 'Remplissez le formulaire ci-dessous' : 'Sélectionnez votre profil pour commencer'}
    </p>
  </div>

  <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-3xl">
    <div class="bg-white py-8 px-4 border border-gray-200 sm:rounded-[3rem] sm:px-10">

      {#if !showForm}
        <UserTypeSelector
          {userTypes}
          {selectedType}
          on:select={(e) => selectType(e.detail)}
          on:next={goToForm}
        />
      {:else}
        <div class="animate-slideIn">
          <!-- Bouton retour -->
          <button
            type="button"
            on:click={goBack}
            class="inline-flex items-center text-sm text-gray-600 hover:text-green-600 mb-6 transition-colors"
          >
            <Icon icon="heroicons:arrow-left" class="h-4 w-4 mr-2" />
            Retour à la sélection
          </button>

          <!-- Indicateur du type sélectionné -->
          <div class="flex items-center gap-3 mb-6 p-3 bg-green-50 rounded-full">
            {#each userTypes as type}
              {#if type.id === activeTab}
                <div class="p-2 rounded-full bg-green-100 text-green-600">
                  <Icon icon={type.icon} class="h-5 w-5" />
                </div>
                <span class="font-medium text-green-700">{type.label}</span>
              {/if}
            {/each}
          </div>

          {#if activeTab === 'etablissement'}
            <EtablissementForm on:success={handleSuccess} />
          {:else if activeTab === 'professeur'}
            <ProfesseurForm on:success={handleSuccess} />
          {:else if activeTab === 'eleve'}
            <EleveForm on:success={handleSuccess} />
          {:else}
            <!-- Message "pas encore disponible" pour les autres types -->
            <div class="animate-fadeIn py-12">
              <div class="flex flex-col items-center text-center">
                <div class="w-20 h-20 rounded-full bg-green-50 flex items-center justify-center mb-6">
                  <Icon icon="heroicons:clock" class="h-10 w-10 text-green-600" />
                </div>
                <h3 class="text-xl font-medium text-gray-900 mb-3">
                  Bientôt disponible
                </h3>
                <p class="text-sm text-gray-600 max-w-md">
                  L'inscription pour le profil
                  <span class="font-medium text-green-700">
                    {userTypes.find((t) => t.id === activeTab)?.label}
                  </span>
                  n'est pas encore disponible. Nous travaillons activement pour vous l'offrir très prochainement.
                </p>
                <div class="mt-8 p-4 bg-gray-50 rounded-2xl border border-gray-200 max-w-md">
                  <p class="text-xs text-gray-500">
                    En attendant, vous pouvez créer un compte en tant qu'établissement.
                  </p>
                </div>
                <button
                  type="button"
                  on:click={goBack}
                  class="mt-6 inline-flex items-center px-6 py-2 bg-green-600 text-white rounded-full text-sm font-medium hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors"
                >
                  <Icon icon="heroicons:arrow-left" class="h-4 w-4 mr-2" />
                  Choisir un autre profil
                </button>
              </div>
            </div>
          {/if}
        </div>
      {/if}

      <div class="mt-6">
        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-300"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-white text-gray-500">
              Déjà un compte ?
            </span>
          </div>
        </div>

        <div class="mt-6">
          <a
            href="/login"
            class="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-full text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            Se connecter
          </a>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  @keyframes slideIn {
    from {
      transform: translateX(30px);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .animate-slideIn {
    animation: slideIn 0.3s ease-out;
  }

  .animate-fadeIn {
    animation: fadeIn 0.3s ease-out;
  }
</style>