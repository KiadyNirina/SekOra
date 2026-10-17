<script>
  import Icon from '@iconify/svelte';
</script>

<section class="relative overflow-hidden min-h-screen">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-0 min-h-screen flex items-center">
    <!-- Two-column layout -->
    <div class="grid lg:grid-cols-2 gap-8 lg:gap-12 items-center w-full">
      
      <!-- Left: text content -->
      <div class="text-center lg:text-left order-2 lg:order-1">
        <h1 class="unbounded text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-extrabold tracking-tight text-gray-900 leading-tight">
          <span class="block">Révolutionnez votre</span>
          <span class="block bg-clip-text text-transparent bg-gradient-to-r from-[#20784d] to-emerald-600">gestion scolaire</span>
        </h1>
        
        <p class="mt-4 sm:mt-6 max-w-2xl mx-auto lg:mx-0 text-base sm:text-lg lg:text-xl text-gray-600">
          eBoss modernise votre établissement avec une plateforme intuitive, complète et conçue pour les besoins éducatifs d'aujourd'hui.
        </p>
        
        <div class="mt-6 sm:mt-8 flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center lg:justify-start">
          <a href="/login" class="px-6 sm:px-8 py-3 sm:py-4 border border-transparent text-base sm:text-lg font-medium rounded-full text-white bg-[#20784d] hover:bg-green-700 transition-all duration-300 transform hover:-translate-y-1">
            Commencer maintenant
          </a>
          <a href="#features" class="px-6 sm:px-8 py-3 sm:py-4 border border-gray-300 text-base sm:text-lg font-medium rounded-full bg-white text-gray-700 hover:border-green-600 transition-all duration-300 flex items-center justify-center">
            <Icon icon="mdi:play-circle-outline" class="mr-2" />
            Voir les fonctionnalités
          </a>
        </div>
      </div>
      
      <!-- Right: the real image -->
      <div class="flex justify-center lg:justify-end order-1 lg:order-2">
        <img 
          src="img/Learning-cuate.svg" 
          alt="Enseignant en classe" 
          class="w-full max-w-xs sm:max-w-sm md:max-w-md lg:max-w-lg object-contain"
        />
      </div>
    </div>
  </div>
</section>