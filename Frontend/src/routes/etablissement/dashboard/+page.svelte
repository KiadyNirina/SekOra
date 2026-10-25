<script>
  import { onMount } from 'svelte';
  import StatsOverview from '../../../components/etablissement/StatsOverview.svelte';
  import RecentActivities from '../../../components/etablissement/RecentActivities.svelte';
  import CalendarOverview from '../../../components/etablissement/CalendarOverview.svelte';
  import { authApi } from '../../../lib/api';

  let stats = {
    students: 0,
    teachers: 0,
    classes: 0,
    pendingPayments: 0,
  };

  let activities = [];
  let activitiesLoading = true;
  let activitiesError = null;

  let etablissementId = null;
  let loading = true;
  let error = null;

  async function loadDashboard() {
    loading = true;
    activitiesLoading = true;
    error = null;
    activitiesError = null;

    try {
      const profile = await authApi.getProfile();
      etablissementId = profile.profile?.id || profile.etablissement?.id;

      if (!etablissementId) {
        throw new Error('Établissement non trouvé');
      }

      // ⬇️ Charge les 5 dernières activités via le nouvel endpoint
      const [eleves, professeurs, classes, activitiesData] = await Promise.all([
        authApi.getEleves({ etablissement: etablissementId, limit: 1 }),
        authApi.getProfesseurs({ etablissement: etablissementId, limit: 1 }),
        authApi.getClasses({ etablissement: etablissementId, limit: 1 }),
        authApi.getActivities({ page_size: 5, days: 90 })
          .catch(err => {
            console.error('Erreur activités:', err);
            activitiesError = err.message || 'Impossible de charger les activités';
            return { results: [] };
          }),
      ]);

      const getCount = (data) => {
        if (!data) return 0;
        if (Array.isArray(data)) return data.length;
        if (data.count !== undefined) return data.count;
        if (data.results && Array.isArray(data.results)) return data.results.length;
        return 0;
      };

      stats = {
        students: getCount(eleves),
        teachers: getCount(professeurs),
        classes: getCount(classes),
        pendingPayments: 12,
      };

      activities = activitiesData.results || [];
    } catch (err) {
      console.error('Erreur lors du chargement du dashboard:', err);
      error = err.message || 'Impossible de charger les données';
    } finally {
      loading = false;
      activitiesLoading = false;
    }
  }

  // Recharge les activités seules (utile pour le bouton "Rafraîchir" du widget)
  async function reloadActivities() {
    activitiesLoading = true;
    activitiesError = null;
    try {
      const data = await authApi.getActivities({ page_size: 5, days: 90 });
      activities = data.results || [];
    } catch (err) {
      activitiesError = err.message || 'Impossible de charger les activités';
    } finally {
      activitiesLoading = false;
    }
  }

  onMount(() => {
    loadDashboard();
  });
</script>

<h1 class="text-2xl font-bold mb-6">Tableau de bord</h1>

{#if loading}
  <div class="flex justify-center items-center h-64">
    <div class="flex flex-col items-center gap-3">
      <div class="w-10 h-10 border-4 border-gray-200 border-t-[#20784d] rounded-full animate-spin"></div>
      <div class="text-gray-500 text-sm">Chargement du tableau de bord…</div>
    </div>
  </div>
{:else if error}
  <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-3" role="alert">
    <span class="flex-1">
      <strong class="font-semibold">Erreur :</strong>
      <span class="block sm:inline">{error}</span>
    </span>
    <button
      on:click={loadDashboard}
      class="px-3 py-1 bg-white hover:bg-red-100 border border-red-200 rounded text-sm font-medium"
    >
      Réessayer
    </button>
  </div>
{:else}
  <StatsOverview {stats} />

  <div class="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
    <CalendarOverview />

    <!-- ⬇️ Widget activités avec lien vers la page complète -->
    <RecentActivities
      {activities}
      loading={activitiesLoading}
      error={activitiesError}
      on:refresh={reloadActivities}
      viewAllHref="/etablissement/activites"
    />
  </div>
{/if}