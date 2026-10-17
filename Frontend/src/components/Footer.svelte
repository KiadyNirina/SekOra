<script>
  import Icon from '@iconify/svelte';
  
  const links = [
    {
      title: 'Produit',
      items: [
        { name: 'Fonctionnalités', href: '#features' },
        // { name: 'Tarifs', href: '#pricing' },
        // { name: 'API', href: '#' },
        { name: 'Nouveautés', href: '#' }
      ]
    },
    /*{
      title: 'Entreprise',
      items: [
        { name: 'À propos', href: '#' },
        { name: 'Blog', href: '#' },
        { name: 'Carrières', href: '#' },
        { name: 'Presse', href: '#' }
      ]
    },*/
    {
      title: 'Ressources',
      items: [
        // { name: 'Documentation', href: '#' },
        { name: 'Guides', href: '#' },
        // { name: 'Support', href: '#' },
        // { name: 'Statut', href: '#' }
      ]
    },
    {
      title: 'Légal',
      items: [
        { name: 'Confidentialité', href: '#' },
        { name: 'Conditions', href: '#' },
        { name: 'Mentions légales', href: '#' }
      ]
    }
  ];
</script>

<footer class="bg-gray-800">
  <div class="max-w-7xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
    <div class="xl:grid xl:grid-cols-3 xl:gap-8">
      <div class="space-y-8 xl:col-span-1">
        <div class="flex items-center">
          <img src="/icons/logo.png" class="h-10" alt="">
        </div>
        <p class="text-gray-300 text-sm">
          La plateforme de gestion scolaire moderne pour les établissements d'enseignement.
        </p>
        <div class="flex space-x-6">
          <a href="#" class="text-gray-400 hover:text-white">
            <Icon icon="akar-icons:facebook-fill" class="h-6 w-6" />
          </a>
          <a href="#" class="text-gray-400 hover:text-white">
            <Icon icon="akar-icons:twitter-fill" class="h-6 w-6" />
          </a>
          <a href="#" class="text-gray-400 hover:text-white">
            <Icon icon="akar-icons:linkedin-box-fill" class="h-6 w-6" />
          </a>
        </div>
      </div>
      <div class="mt-12 grid grid-cols-2 gap-8 xl:mt-0 xl:col-span-2">
        {#each links as link}
          <div>
            <h3 class="text-sm font-semibold text-gray-300 tracking-wider uppercase">
              {link.title}
            </h3>
            <ul class="mt-4 space-y-1">
              {#each link.items as item}
                <li>
                  <a href={item.href} class="text-sm text-gray-400 hover:text-white">
                    {item.name}
                  </a>
                </li>
              {/each}
            </ul>
          </div>
        {/each}
      </div>
    </div>
    <div class="mt-12 border-t border-gray-700 pt-8">
      <p class="text-sm text-gray-400 text-center">
        &copy; {new Date().getFullYear()} SekOra. Tous droits réservés.
      </p>
    </div>
  </div>
</footer>