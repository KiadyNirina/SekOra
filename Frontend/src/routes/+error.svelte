<script>
  import { page } from '$app/stores';
  import Icon from '@iconify/svelte';

  // Récupère le statut HTTP de l'erreur
  $: status = $page.status || 500;

  // Mapping des erreurs courantes
  const errorMap = {
    400: {
      title: 'Requête invalide',
      description: 'La requête envoyée n\'est pas valide. Vérifiez les données et réessayez.',
      icon: 'heroicons:exclamation-triangle',
      color: 'amber',
    },
    401: {
      title: 'Non authentifié',
      description: 'Vous devez être connecté pour accéder à cette page.',
      icon: 'heroicons:lock-closed',
      color: 'amber',
    },
    403: {
      title: 'Accès refusé',
      description: 'Vous n\'avez pas les permissions nécessaires pour accéder à cette ressource.',
      icon: 'heroicons:shield-exclamation',
      color: 'red',
    },
    404: {
      title: 'Page introuvable',
      description: 'La page que vous cherchez n\'existe pas ou a été déplacée.',
      icon: 'heroicons:magnifying-glass',
      color: 'blue',
    },
    500: {
      title: 'Erreur serveur',
      description: 'Une erreur inattendue s\'est produite. Notre équipe a été notifiée.',
      icon: 'heroicons:server-stack',
      color: 'red',
    },
    503: {
      title: 'Service indisponible',
      description: 'Le service est temporairement indisponible. Réessayez dans quelques instants.',
      icon: 'heroicons:wrench-screwdriver',
      color: 'amber',
    },
  };

  // Récupère les infos selon le status, ou fallback générique
  $: errorInfo = errorMap[status] || {
    title: 'Une erreur est survenue',
    description: $page.error?.message || 'Une erreur inattendue s\'est produite.',
    icon: 'heroicons:exclamation-circle',
    color: 'red',
  };

  // Couleurs Tailwind selon le type d'erreur
  const colorClasses = {
    blue:  { bg: 'bg-blue-50',  border: 'border-blue-200',  text: 'text-blue-700',  iconBg: 'bg-blue-100',  iconText: 'text-blue-600' },
    amber: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', iconBg: 'bg-amber-100', iconText: 'text-amber-600' },
    red:   { bg: 'bg-red-50',   border: 'border-red-200',   text: 'text-red-700',   iconBg: 'bg-red-100',   iconText: 'text-red-600' },
  };

  $: colors = colorClasses[errorInfo.color] || colorClasses.red;

  function goBack() {
    if (typeof window !== 'undefined' && window.history.length > 1) {
      window.history.back();
    } else {
      window.location.href = '/';
    }
  }

  function reload() {
    if (typeof window !== 'undefined') {
      window.location.reload();
    }
  }
</script>

<svelte:head>
  <title>{status} — {errorInfo.title}</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-12">
  <div class="w-full max-w-lg">

    <!-- Carte principale -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">

      <!-- Barre colorée en haut -->
      <div class="h-1.5 w-full {errorInfo.color === 'red' ? 'bg-red-500' : errorInfo.color === 'amber' ? 'bg-amber-500' : 'bg-blue-500'}"></div>

      <div class="p-8 text-center">

        <!-- Icône -->
        <div class="mx-auto w-20 h-20 {colors.iconBg} rounded-full flex items-center justify-center mb-6">
          <Icon icon={errorInfo.icon} class="h-10 w-10 {colors.iconText}" />
        </div>

        <!-- Code d'erreur -->
        <p class="text-sm font-semibold {colors.text} tracking-wide uppercase mb-2">
          Erreur {status}
        </p>

        <!-- Titre -->
        <h1 class="text-2xl font-bold text-gray-900 mb-3">
          {errorInfo.title}
        </h1>

        <!-- Description -->
        <p class="text-sm text-gray-600 mb-6 leading-relaxed">
          {errorInfo.description}
        </p>

        <!-- Message détaillé (en dev uniquement) -->
        {#if $page.error?.message && $page.error.message !== errorInfo.description}
          <div class="mb-6 p-3 {colors.bg} border {colors.border} rounded-lg text-left">
            <p class="text-xs font-mono {colors.text} break-words">
              {$page.error.message}
            </p>
          </div>
        {/if}

        <!-- Actions -->
        <div class="flex flex-col sm:flex-row items-center justify-center gap-3">
          <button
            on:click={goBack}
            class="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Icon icon="heroicons:arrow-left" class="h-4 w-4" />
            Retour
          </button>

          <button
            on:click={reload}
            class="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 text-sm font-medium text-white bg-[#20784d] rounded-lg hover:bg-[#1a633f] transition-colors"
          >
            <Icon icon="heroicons:arrow-path" class="h-4 w-4" />
            Réessayer
          </button>

          <a
            href="/"
            class="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 text-sm font-medium text-[#20784d] bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
          >
            <Icon icon="heroicons:home" class="h-4 w-4" />
            Accueil
          </a>
        </div>
      </div>

      <!-- Footer avec code technique -->
      <div class="px-8 py-4 bg-gray-50 border-t border-gray-100">
        <p class="text-xs text-gray-400 text-center">
          Statut HTTP <span class="font-mono font-semibold text-gray-500">{status}</span>
          {#if $page.url?.pathname}
            · <span class="font-mono text-gray-400">{$page.url.pathname}</span>
          {/if}
        </p>
      </div>
    </div>

    <!-- Aide supplémentaire -->
    <div class="mt-6 text-center">
      <p class="text-xs text-gray-500">
        Si le problème persiste, contactez le support en précisant le code d'erreur.
      </p>
    </div>

  </div>
</div>