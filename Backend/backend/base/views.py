from rest_framework import generics, viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
import csv
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, F, Value, ExpressionWrapper, FloatField
from django.db.models.functions import ACos, Cos, Radians, Sin
from django.utils import timezone
from django.core.management import call_command
from .serializers import (
    CustomTokenObtainPairSerializer,
    EtablissementSerializer, 
    ProfesseurSerializer, 
    EleveSerializer, 
    ParentSerializer,
    UserProfileSerializer,
    AnneeScolaireSerializer,
    ClasseSerializer,
    MatiereSerializer,
    SalleSerializer,
    CoursSerializer,
    PeriodeSerializer,
    EvaluationSerializer,
    EvaluationDetailSerializer,
    NoteSerializer,
)
from .models import *
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import time
from django.conf import settings
import socket
import urllib3.util.connection as urllib3_cn
from datetime import timedelta

def _allowed_gai_family():
    return socket.AF_INET

urllib3_cn.allowed_gai_family = _allowed_gai_family

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@csrf_exempt
def geocode_proxy(request):
    """
    Proxy pour les requêtes de géocodage vers Nominatim
    """
    if request.method == 'GET':
        query = request.GET.get('q', '')
        format_type = request.GET.get('format', 'json')
        limit = request.GET.get('limit', 1)
        
        if not query:
            return JsonResponse({'error': 'Query parameter "q" is required'}, status=400)
        
        try:
            # Appel à Nominatim depuis le serveur
            url = 'https://nominatim.openstreetmap.org/search'
            params = {
                'q': query,
                'format': format_type,
                'limit': limit,
                'addressdetails': 1,
                'accept-language': 'fr'
            }
            
            headers = {
                'User-Agent': 'VotreApplication/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return JsonResponse(response.json(), safe=False)
            else:
                return JsonResponse(
                    {'error': f'Erreur Nominatim: {response.status_code}'},
                    status=response.status_code
                )
                
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def reverse_geocode_proxy(request):
    """
    Proxy pour le géocodage inverse vers Nominatim
    """
    if request.method == 'GET':
        lat = request.GET.get('lat')
        lon = request.GET.get('lon')
        
        if not lat or not lon:
            return JsonResponse({'error': 'Latitude and longitude required'}, status=400)
        
        try:
            url = 'https://nominatim.openstreetmap.org/reverse'
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'addressdetails': 1,
                'accept-language': 'fr'
            }
            
            headers = {
                'User-Agent': 'Sekora/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return JsonResponse(response.json(), safe=False)
            else:
                return JsonResponse(
                    {'error': f'Erreur Nominatim: {response.status_code}'},
                    status=response.status_code
                )
                
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def nearby_schools_proxy(request):
    """
    Retourne TOUTES les écoles OSM depuis la BDD locale.
    Le filtrage par distance est fait côté frontend (si besoin).
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    TYPE_MAPPING = {
        'school': 'ecole',
        'college': 'college',
        'lycee': 'lycee',
        'university': 'universite',
        'kindergarten': 'ecole',
    }

    qs = EcoleOSM.objects.all().order_by('nom')

    schools = []
    for e in qs:
        schools.append({
            'id': e.osm_id,
            'name': e.nom or 'École sans nom',
            'address': e.adresse or None,
            'lat': e.latitude,
            'lng': e.longitude,
            'type': TYPE_MAPPING.get(e.type_ecole, 'ecole'),
            'source': 'osm',
        })

    return JsonResponse({
        'count': len(schools),
        'results': schools,
    })
    
class EtablissementViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les établissements avec géolocalisation
    """
    queryset = Etablissement.objects.all().select_related('user')
    serializer_class = EtablissementSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtres de base
        type_etablissement = self.request.query_params.get('type')
        search = self.request.query_params.get('search')
        
        if type_etablissement:
            queryset = queryset.filter(type_etablissement=type_etablissement)
        
        if search:
            queryset = queryset.filter(
                Q(nom__icontains=search) |
                Q(adresse__icontains=search) |
                Q(user__email__icontains=search)
            )
        
        # Filtrage par proximité (calcul avec Haversine)
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        radius = self.request.query_params.get('radius', 10)
        
        if lat and lng:
            try:
                lat = float(lat)
                lng = float(lng)
                radius = float(radius)
                
                # Calcul de distance avec Haversine
                rad_lat = Radians(Value(lat))
                rad_lng = Radians(Value(lng))
                rad_est_lat = Radians(F('latitude'))
                rad_est_lng = Radians(F('longitude'))
                
                distance_expr = ExpressionWrapper(
                    6371 * ACos(
                        Cos(rad_lat) * Cos(rad_est_lat) *
                        Cos(rad_est_lng - rad_lng) +
                        Sin(rad_lat) * Sin(rad_est_lat)
                    ),
                    output_field=FloatField()
                )
                
                queryset = queryset.annotate(
                    distance=distance_expr
                ).filter(
                    distance__lte=radius,
                    latitude__isnull=False,
                    longitude__isnull=False
                ).order_by('distance')
                
            except (ValueError, TypeError):
                pass
        
        # Filtrer les établissements avec/sans coordonnées
        only_with_coords = self.request.query_params.get('with_coords', 'false')
        if only_with_coords.lower() == 'true':
            queryset = queryset.exclude(
                Q(latitude__isnull=True) | Q(longitude__isnull=True)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """
        Endpoint pour trouver les établissements proches
        """
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = request.query_params.get('radius', 10)
        
        if not lat or not lng:
            return Response({
                'error': 'Les paramètres lat et lng sont requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            lat = float(lat)
            lng = float(lng)
            radius = float(radius)
            
            queryset = self.get_queryset()
            
            # Si pas déjà annoté avec distance
            if 'distance' not in queryset.query.annotations:
                rad_lat = Radians(Value(lat))
                rad_lng = Radians(Value(lng))
                rad_est_lat = Radians(F('latitude'))
                rad_est_lng = Radians(F('longitude'))
                
                distance_expr = ExpressionWrapper(
                    6371 * ACos(
                        Cos(rad_lat) * Cos(rad_est_lat) *
                        Cos(rad_est_lng - rad_lng) +
                        Sin(rad_lat) * Sin(rad_est_lat)
                    ),
                    output_field=FloatField()
                )
                
                queryset = queryset.annotate(
                    distance=distance_expr
                ).filter(
                    distance__lte=radius,
                    latitude__isnull=False,
                    longitude__isnull=False
                ).order_by('distance')
            
            serializer = self.get_serializer(queryset, many=True)
            
            return Response({
                'count': queryset.count(),
                'results': serializer.data,
                'center': {'lat': lat, 'lng': lng},
                'radius': radius
            })
            
        except ValueError:
            return Response({
                'error': 'Latitude et longitude doivent être des nombres valides'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def update_coordinates_batch(self, request):
        """
        Met à jour les coordonnées en lot depuis les données frontend
        """
        establishments_data = request.data.get('establishments', [])
        
        if not establishments_data:
            return Response({
                'error': 'Aucune donnée fournie'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        results = []
        for est_data in establishments_data:
            est_id = est_data.get('id')
            latitude = est_data.get('latitude')
            longitude = est_data.get('longitude')
            
            if not est_id or latitude is None or longitude is None:
                results.append({
                    'id': est_id,
                    'success': False,
                    'error': 'Données incomplètes'
                })
                continue
            
            try:
                establishment = Etablissement.objects.get(id=est_id)
                establishment.latitude = float(latitude)
                establishment.longitude = float(longitude)
                establishment.coordinates_verified = True
                establishment.coordinates_updated_at = timezone.now()
                establishment.save()
                
                results.append({
                    'id': est_id,
                    'success': True,
                    'latitude': establishment.latitude,
                    'longitude': establishment.longitude
                })
            except Etablissement.DoesNotExist:
                results.append({
                    'id': est_id,
                    'success': False,
                    'error': 'Établissement non trouvé'
                })
            except Exception as e:
                results.append({
                    'id': est_id,
                    'success': False,
                    'error': str(e)
                })
        
        success_count = sum(1 for r in results if r['success'])
        
        return Response({
            'message': f'{success_count} établissements mis à jour sur {len(results)}',
            'total': len(results),
            'success': success_count,
            'failed': len(results) - success_count,
            'results': results
        })
    
    @action(detail=True, methods=['post'])
    def verify_coordinates(self, request, pk=None):
        """
        Vérifie et valide les coordonnées d'un établissement
        """
        establishment = self.get_object()
        
        if not establishment.has_coordinates:
            return Response({
                'error': 'Cet établissement n\'a pas de coordonnées'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Marquer comme vérifié
        establishment.coordinates_verified = True
        establishment.coordinates_updated_at = timezone.now()
        establishment.save()
        
        return Response({
            'success': True,
            'message': 'Coordonnées vérifiées',
            'latitude': establishment.latitude,
            'longitude': establishment.longitude,
            'verified': establishment.coordinates_verified
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Statistiques sur les coordonnées des établissements
        """
        total = Etablissement.objects.count()
        with_coords = Etablissement.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).count()
        verified = Etablissement.objects.filter(
            coordinates_verified=True
        ).count()
        
        return Response({
            'total': total,
            'with_coordinates': with_coords,
            'without_coordinates': total - with_coords,
            'verified': verified,
            'percentage_with_coords': round((with_coords / total * 100) if total > 0 else 0, 2),
            'percentage_verified': round((verified / total * 100) if total > 0 else 0, 2)
        })


class EtablissementRegistrationView(generics.CreateAPIView):
    serializer_class = EtablissementSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        print("Données reçues:", request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        etablissement = serializer.save()
        
        # Génération du token
        user = etablissement.user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "message": "Inscription réussie pour l'établissement",
            "etablissement": {
                "id": etablissement.id,
                "nom": etablissement.nom,
                "type_etablissement": etablissement.type_etablissement,
                "adresse": etablissement.adresse,
                "latitude": etablissement.latitude,
                "longitude": etablissement.longitude,
                "coordinates_verified": etablissement.coordinates_verified
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

class AnneeScolaireViewSet(viewsets.ModelViewSet):
    serializer_class = AnneeScolaireSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'etablissement'):
            return AnneeScolaire.objects.filter(
                etablissement=self.request.user.etablissement
            ).order_by('-date_debut')
        return AnneeScolaire.objects.none()

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'etablissement'):
            raise PermissionError("Seul un établissement peut créer une année scolaire")
        serializer.save(etablissement=self.request.user.etablissement)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        annee = self.get_object()

        # Désactive les autres années du MÊME établissement uniquement
        AnneeScolaire.objects.filter(
            etablissement=annee.etablissement
        ).exclude(pk=pk).update(est_active=False)

        annee.est_active = True
        annee.save()

        return Response({'status': 'année scolaire activée'})

    @action(detail=False, methods=['get'])
    def current(self, request):
        if not hasattr(request.user, 'etablissement'):
            return Response(
                {'detail': 'Utilisateur non établissement'},
                status=status.HTTP_403_FORBIDDEN
            )

        annee_active = AnneeScolaire.objects.filter(
            etablissement=request.user.etablissement,
            est_active=True
        ).first()

        if not annee_active:
            return Response(
                {'detail': 'Aucune année scolaire active'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(self.get_serializer(annee_active).data)

class ClasseViewSet(viewsets.ModelViewSet):
    serializer_class = ClasseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        etablissement_id = self.request.query_params.get('etablissement')
        queryset = Classe.objects.all()
        if etablissement_id:
            queryset = queryset.filter(etablissement_id=etablissement_id)
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        instance = self.get_object()
        new_annee = serializer.validated_data.get('annee_scolaire', instance.annee_scolaire)
        
        if new_annee != instance.annee_scolaire:
            if new_annee.etablissement_id != instance.etablissement_id:
                raise serializers.ValidationError({
                    'annee_scolaire': "Cette année scolaire n'appartient pas à l'établissement"
                })
        
        serializer.save()

class MatiereViewSet(viewsets.ModelViewSet):
    serializer_class = MatiereSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Matiere.objects.select_related(
            'etablissement', 'annee_scolaire'
        ).prefetch_related(
            'classes',
            'classes__annee_scolaire',
        )

        etablissement_id = self.request.query_params.get('etablissement')
        annee_scolaire_id = self.request.query_params.get('annee_scolaire')
        search = self.request.query_params.get('search')

        # Si l'utilisateur est un établissement, restreindre à son périmètre
        if hasattr(self.request.user, 'etablissement'):
            queryset = queryset.filter(
                etablissement=self.request.user.etablissement
            )
        elif etablissement_id:
            queryset = queryset.filter(etablissement_id=etablissement_id)

        if annee_scolaire_id:
            queryset = queryset.filter(annee_scolaire_id=annee_scolaire_id)

        if search:
            queryset = queryset.filter(nom__icontains=search)

        return queryset.order_by('nom')

    def perform_create(self, serializer):
        # Force l'établissement de l'utilisateur connecté
        if hasattr(self.request.user, 'etablissement'):
            serializer.save(etablissement=self.request.user.etablissement)
        else:
            serializer.save()
    
class SalleViewSet(viewsets.ModelViewSet):
    serializer_class = SalleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'etablissement'):
            return Salle.objects.filter(
                etablissement=self.request.user.etablissement
            )

        return Salle.objects.none()
    
class CoursViewSet(viewsets.ModelViewSet):
    serializer_class = CoursSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Cours.objects.select_related(
            'classe',
            'professeur__user',
            'matiere',
            'salle',
            'annee_scolaire'
        )

        if hasattr(self.request.user, 'etablissement'):
            queryset = queryset.filter(
                etablissement=self.request.user.etablissement
            )
        else:
            return queryset.none()

        classe = self.request.query_params.get('classe')
        professeur = self.request.query_params.get('professeur')
        matiere = self.request.query_params.get('matiere')
        annee = self.request.query_params.get('annee')
        jour = self.request.query_params.get('jour')

        if classe:
            queryset = queryset.filter(classe_id=classe)

        if professeur:
            queryset = queryset.filter(professeur_id=professeur)

        if matiere:
            queryset = queryset.filter(matiere_id=matiere)

        if annee:
            queryset = queryset.filter(
                annee_scolaire_id=annee
            )

        if jour:
            queryset = queryset.filter(
                jour=jour
            )

        return queryset.order_by(
            'jour',
            'heure_debut'
        )

class PeriodeViewSet(viewsets.ModelViewSet):
    """Liste les périodes pour les filtres (lecture seule)"""
    serializer_class = PeriodeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Periode.objects.select_related('annee_scolaire')

        # Filtrer par établissement de l'utilisateur connecté
        if hasattr(self.request.user, 'etablissement'):
            queryset = queryset.filter(
                etablissement=self.request.user.etablissement
            )
        else:
            return Periode.objects.none()

        # Filtrer par année scolaire active si demandé
        annee_active = self.request.query_params.get('annee_active')
        if annee_active:
            queryset = queryset.filter(annee_scolaire__est_active=True)

        return queryset.order_by('annee_scolaire', 'ordre')
    
    def perform_create(self, serializer):
        # Force l'établissement à celui de l'utilisateur connecté
        if hasattr(self.request.user, 'etablissement'):
            serializer.save(etablissement=self.request.user.etablissement)
        else:
            raise PermissionError("Établissement requis")


class EvaluationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EvaluationDetailSerializer
        return EvaluationSerializer

    def get_queryset(self):
        queryset = Evaluation.objects.select_related(
            'matiere', 'classe', 'professeur__user', 'periode', 'etablissement'
        ).prefetch_related('notes')

        # Filtrer par établissement de l'utilisateur connecté
        if hasattr(self.request.user, 'etablissement'):
            queryset = queryset.filter(
                etablissement=self.request.user.etablissement
            )
        else:
            return Evaluation.objects.none()

        # Filtres additionnels
        classe = self.request.query_params.get('classe')
        matiere = self.request.query_params.get('matiere')
        periode = self.request.query_params.get('periode')
        professeur = self.request.query_params.get('professeur')
        annee = self.request.query_params.get('annee')
        statut = self.request.query_params.get('statut')
        search = self.request.query_params.get('search')

        if classe:
            queryset = queryset.filter(classe_id=classe)
        if matiere:
            queryset = queryset.filter(matiere_id=matiere)
        if periode:
            queryset = queryset.filter(periode_id=periode)
        if professeur:
            queryset = queryset.filter(professeur_id=professeur)
        if annee:
            queryset = queryset.filter(periode__annee_scolaire_id=annee)
        if statut:
            queryset = queryset.filter(statut=statut)
        if search:
            queryset = queryset.filter(
                Q(nom__icontains=search) |
                Q(matiere__nom__icontains=search) |
                Q(classe__nom__icontains=search)
            )

        return queryset.order_by('-date')

    def perform_create(self, serializer):
        # Récupérer l'établissement de l'utilisateur
        if hasattr(self.request.user, 'etablissement'):
            serializer.save(etablissement=self.request.user.etablissement)
        else:
            raise PermissionError("Seul un établissement peut créer une évaluation")

    @action(detail=True, methods=['post'])
    def manage_notes(self, request, pk=None):
        """
        Met à jour / crée les notes pour une évaluation.
        Attendu : { "notes": [ { "eleve": 1, "note": 15.5, "appreciation": "...", "absent": false }, ... ] }
        """
        evaluation = self.get_object()
        notes_data = request.data.get('notes', [])

        results = []
        for note_data in notes_data:
            eleve_id = note_data.get('eleve')
            note_value = note_data.get('note')
            appreciation = note_data.get('appreciation', '')
            absent = note_data.get('absent', False)

            if not eleve_id:
                continue

            # Vérifier que l'élève appartient à la classe de l'évaluation
            try:
                eleve = Eleve.objects.get(id=eleve_id, classe=evaluation.classe)
            except Eleve.DoesNotExist:
                results.append({'eleve': eleve_id, 'error': 'Élève non trouvé dans la classe'})
                continue

            note, created = Note.objects.update_or_create(
                evaluation=evaluation,
                eleve=eleve,
                defaults={
                    'note': note_value,
                    'appreciation': appreciation,
                    'absent': absent
                }
            )
            results.append({
                'eleve': eleve_id,
                'note': note.note,
                'created': created,
                'absent': note.absent
            })

        evaluation.refresh_from_db()
        return Response({
            'status': 'notes sauvegardées',
            'results': results
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def publier(self, request, pk=None):
        evaluation = self.get_object()
        evaluation.statut = 'publie'
        evaluation.save()
        return Response({'status': 'évaluation publiée'})

    @action(detail=True, methods=['post'])
    def brouillon(self, request, pk=None):
        evaluation = self.get_object()
        evaluation.statut = 'brouillon'
        evaluation.save()
        return Response({'status': 'évaluation remise en brouillon'})

class ProfesseurRegistrationView(generics.CreateAPIView):
    serializer_class = ProfesseurSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        user = serializer.instance.user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "message": "Inscription réussie pour le professeur",
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED, headers=headers)

class ProfesseurViewSet(viewsets.ModelViewSet):
    queryset = Professeur.objects.all().select_related('user', 'etablissement').prefetch_related('classes','matieres')
    serializer_class = ProfesseurSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset()

        if hasattr(self.request.user, 'etablissement'):
            queryset = queryset.filter(
                etablissement=self.request.user.etablissement
            )
        else:
            return queryset.none()

        search = self.request.query_params.get('search')
        matiere = self.request.query_params.get('matiere')
        classe = self.request.query_params.get('classe')
        annee = self.request.query_params.get('annee')

        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search)
            )
        if matiere:
            queryset = queryset.filter(
                matieres__id=matiere
            ).distinct()

        if classe:
            queryset = queryset.filter(
                classes__id=classe
            ).distinct()

        if annee:
            queryset = queryset.filter(
                classes__annee_scolaire__id=annee
            ).distinct()

        return queryset

    @action(detail=False, methods=['get'])
    def filter_options(self, request):

        if not hasattr(request.user, 'etablissement'):
            return Response(
                {'error': 'Établissement requis'},
                status=400
            )

        etablissement = request.user.etablissement

        professeurs = Professeur.objects.filter(
            etablissement=etablissement
        )

        matieres = Matiere.objects.filter(
            etablissement=etablissement
        )

        classes = Classe.objects.filter(
            etablissement=etablissement
        ).select_related(
            'annee_scolaire'
        )

        annees = AnneeScolaire.objects.filter(
            etablissement=etablissement
        )

        return Response({
            'matieres': [
                {
                    'value': m.id,
                    'label': m.nom
                }
                for m in matieres if m
            ],
            'classes': [
                {
                    'value': c.id,
                    'label': f"{c.nom} ({c.annee_scolaire.nom})"
                }
                for c in classes
            ],
            'annees': [
                {
                    'value': a.id,
                    'label': a.nom
                }
                for a in annees
            ]
        })

class EleveRegistrationView(generics.CreateAPIView):
    serializer_class = EleveSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        user = serializer.instance.user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "message": "Inscription réussie pour l'élève",
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED, headers=headers)

class EleveViewSet(viewsets.ModelViewSet):
    queryset = Eleve.objects.all().select_related('user', 'etablissement', 'classe')
    serializer_class = EleveSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        classe_id = self.request.query_params.get('classe')
        statut = self.request.query_params.get('statut')
        etablissement_id = self.request.query_params.get('etablissement')

        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search)
            )
        if classe_id:
            queryset = queryset.filter(classe_id=classe_id)
        if statut:
            queryset = queryset.filter(statut=statut)
        if etablissement_id:
            queryset = queryset.filter(etablissement_id=etablissement_id)

        return queryset

    @action(detail=False, methods=['get'])
    def filter_options(self, request):
        etablissement_id = request.query_params.get('etablissement')
        
        if not etablissement_id and hasattr(request.user, 'etablissement'):
            etablissement_id = request.user.etablissement.id

        if not etablissement_id:
            return Response({'error': 'Établissement requis'}, status=400)

        classes = Classe.objects.filter(
            etablissement_id=etablissement_id
        ).distinct().values('id', 'nom', 'annee_scolaire__nom')

        annees = AnneeScolaire.objects.filter(
            etablissement__id=etablissement_id
        ).distinct().values('id', 'nom')

        return Response({
            'classes': [{
                'value': c['id'],
                'label': f"{c['nom']} ({c['annee_scolaire__nom']})" 
            } for c in classes],
            'annees': [{
                'value': a['id'],
                'label': a['nom']
            } for a in annees],
            'statuts': [{
                'value': choice[0], 
                'label': choice[1]
            } for choice in Eleve.STATUS_CHOICES]
        })

    @action(detail=False, methods=['post'])
    def bulk(self, request):
        action_type = request.data.get('action')
        ids = request.data.get('ids', [])

        if not ids:
            return Response({'error': 'Aucun étudiant sélectionné'}, status=status.HTTP_400_BAD_REQUEST)

        if action_type == 'delete':
            # Récupérer les élèves sélectionnés avec leur user
            eleves = Eleve.objects.filter(id__in=ids).select_related('user')
            # Supprimer les utilisateurs associés
            for eleve in eleves:
                if eleve.user:
                    eleve.user.delete()
            # Supprimer les élèves (si user est supprimé avec cascade)
            eleves.delete()
            return Response({'message': f'{len(ids)} étudiants et leurs comptes utilisateurs ont été supprimés'}, status=status.HTTP_200_OK)
        elif action_type == 'export':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="etudiants.csv"'
            writer = csv.writer(response)
            writer.writerow(['ID', 'Prénom', 'Nom', 'Email', 'Téléphone', 'Classe', 'Statut', 'Établissement'])
            for eleve in Eleve.objects.filter(id__in=ids).select_related('user', 'etablissement', 'classe'):
                writer.writerow([
                    eleve.id,
                    eleve.user.first_name,
                    eleve.user.last_name,
                    eleve.user.email,
                    eleve.user.telephone,
                    eleve.classe.nom if eleve.classe else '',
                    eleve.get_statut_display(),
                    eleve.etablissement.nom if eleve.etablissement else ''
                ])
            return response
        else:
            return Response({'error': 'Action non valide'}, status=status.HTTP_400_BAD_REQUEST)

class ParentRegistrationView(generics.CreateAPIView):
    serializer_class = ParentSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        user = serializer.instance.user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "message": "Inscription réussie pour le parent",
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED, headers=headers)

class ParentViewSet(viewsets.ModelViewSet):
    queryset = Parent.objects.all().select_related('user').prefetch_related('enfants')
    serializer_class = ParentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
class ImportOSMSchoolsView(APIView):
    """
    Lance manuellement l'import des écoles depuis OpenStreetMap.
    Accessible uniquement aux utilisateurs administrateurs.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            call_command(
                'import_osm_schools',
                lat=-18.92018507,
                lng=47.53656268,
                radius=5000
            )

            return Response({
                'success': True,
                'message': 'Import OSM terminé.'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
class RecentActivityView(APIView):
    """
    Retourne les activités récentes de l'établissement connecté.
    Agrège élèves récents, évaluations publiées, notes ajoutées.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'etablissement'):
            return Response(
                {'error': 'Établissement requis'},
                status=status.HTTP_403_FORBIDDEN
            )

        etablissement = request.user.etablissement
        limit = int(request.query_params.get('limit', 10))
        activities = []

        # ---------- 1. Nouveaux élèves (30 derniers jours) ----------
        recent_students = Eleve.objects.filter(
            etablissement=etablissement,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).select_related('user', 'classe').order_by('-created_at')[:limit]

        for eleve in recent_students:
            activities.append({
                'type': 'new_student',
                'name': eleve.user.get_full_name() or eleve.user.email,
                'class': eleve.classe.nom if eleve.classe else 'Non assigné',
                'date': eleve.created_at.isoformat(),
                'timestamp': eleve.created_at,
            })

        # ---------- 2. Évaluations publiées récemment ----------
        recent_evaluations = Evaluation.objects.filter(
            etablissement=etablissement,
            statut='publie',
            updated_at__gte=timezone.now() - timedelta(days=30)
        ).select_related('classe', 'matiere', 'professeur__user').order_by('-updated_at')[:limit]

        for ev in recent_evaluations:
            activities.append({
                'type': 'grade',
                'name': f"{ev.nom} — {ev.matiere.nom}",
                'class': ev.classe.nom,
                'date': ev.updated_at.isoformat(),
                'timestamp': ev.updated_at,
            })

        # ---------- 3. Professeurs ajoutés récemment ----------
        recent_profs = Professeur.objects.filter(
            etablissement=etablissement,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).select_related('user').order_by('-created_at')[:limit]

        for prof in recent_profs:
            activities.append({
                'type': 'new_teacher',
                'name': prof.user.get_full_name() or prof.user.email,
                'class': '-',
                'date': prof.created_at.isoformat(),
                'timestamp': prof.created_at,
            })

        # ---------- 4. Classes créées récemment ----------
        recent_classes = Classe.objects.filter(
            etablissement=etablissement,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).order_by('-created_at')[:limit]

        for classe in recent_classes:
            activities.append({
                'type': 'new_class',
                'name': classe.nom,
                'class': classe.niveau,
                'date': classe.created_at.isoformat(),
                'timestamp': classe.created_at,
            })

        # ---------- Tri final par date décroissante ----------
        activities.sort(key=lambda a: a['timestamp'], reverse=True)
        activities = activities[:limit]

        # ---------- Formatage de la date relative ----------
        for act in activities:
            act['time'] = self._format_relative_time(act['timestamp'])
            del act['timestamp']  # retire le datetime pour éviter le problème JSON

        return Response({
            'count': len(activities),
            'results': activities,
        })

    @staticmethod
    def _format_relative_time(dt):
        """Formate une date en 'il y a X minutes/heures/jours'."""
        now = timezone.now()
        diff = now - dt

        seconds = diff.total_seconds()
        if seconds < 60:
            return "à l'instant"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"il y a {minutes} min"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"il y a {hours} h"
        elif seconds < 604800:
            days = int(seconds // 86400)
            return f"il y a {days} j"
        else:
            return dt.strftime('%d/%m/%Y')