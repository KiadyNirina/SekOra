from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'annees-scolaires', AnneeScolaireViewSet, basename='anneescolaire')
router.register(r'classes', ClasseViewSet, basename='classe')
router.register(r'eleves', EleveViewSet, basename='eleve')
router.register(r'professeurs', ProfesseurViewSet, basename='professeur')
router.register(r'matieres', MatiereViewSet, basename='matiere')
router.register(r'salles', SalleViewSet, basename='salle')
router.register(r'cours', CoursViewSet, basename='cours')
router.register(r'etablissements', EtablissementViewSet, basename='etablissement') 
router.register(r'periodes', PeriodeViewSet, basename='periode')
router.register(r'evaluations', EvaluationViewSet, basename='evaluation')

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('register/etablissement/', EtablissementRegistrationView.as_view(), name='register-etablissement'),
    path('register/professeur/', ProfesseurRegistrationView.as_view(), name='register-professeur'),
    path('register/eleve/', EleveRegistrationView.as_view(), name='register-eleve'),
    path('register/parent/', ParentRegistrationView.as_view(), name='register-parent'),

    path('profile/', UserProfileView.as_view(), name='profile'),
    
    path('api/', include(router.urls)),
    path('api/geocode/', geocode_proxy, name='geocode-proxy'),
    path('api/reverse-geocode/', reverse_geocode_proxy, name='reverse-geocode-proxy'),
    path('api/nearby/', nearby_schools_proxy, name='nearby-schools'),
    path('admin/import-osm/', ImportOSMSchoolsView.as_view(), name='import-osm-schools'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )