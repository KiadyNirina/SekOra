from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Etablissement, Professeur, Eleve, Parent, AnneeScolaire, Classe, Matiere, Salle, Cours, Periode, Evaluation, Note
from django.utils import timezone
from django.db.models import Avg

class TimeStampedSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        fields = ['created_at', 'updated_at']
        
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email_or_username = attrs.get('email') or attrs.get('username')
        
        if not email_or_username:
            raise serializers.ValidationError("Email ou nom d'utilisateur requis")
        
        user = authenticate(
            request=self.context.get('request'),
            username=email_or_username,
            password=attrs.get('password')
        )
        
        if not user:
            raise serializers.ValidationError("Identifiants invalides")
        
        if not user.is_active:
            raise serializers.ValidationError("Ce compte est désactivé")
        
        refresh = self.get_token(user)
        
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'email': user.email,
            'user_type': user.user_type,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
        
        return data

class AnneeScolaireSerializer(serializers.ModelSerializer):
    est_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AnneeScolaire
        fields = ['id', 'nom', 'date_debut', 'date_fin', 'est_active', 'etablissement', 'created_at', 'updated_at',]
        read_only_fields = ['id', 'etablissement', 'created_at', 'updated_at']

class ClasseSerializer(serializers.ModelSerializer):
    annee_scolaire = AnneeScolaireSerializer(read_only=True)
    annee_scolaire_id = serializers.PrimaryKeyRelatedField(
        queryset=AnneeScolaire.objects.all(),
        source='annee_scolaire',
        write_only=True
    )
    
    class Meta:
        model = Classe
        fields = '__all__'
    
    def validate(self, data):
        etablissement = data.get('etablissement') or (self.instance.etablissement if self.instance else None)
        annee_scolaire = data.get('annee_scolaire') or (self.instance.annee_scolaire if self.instance else None)
        matieres = data.get('matieres')

        if etablissement and annee_scolaire:
            if annee_scolaire.etablissement_id != etablissement.id:
                raise serializers.ValidationError({
                    'annee_scolaire': "Cette année scolaire n'appartient pas à cet établissement"
                })

        if matieres is not None and annee_scolaire:
            for matiere in matieres:
                if matiere.annee_scolaire_id and matiere.annee_scolaire_id != annee_scolaire.id:
                    raise serializers.ValidationError({
                        'matieres': (
                            f"La matière « {matiere.nom} » appartient à une autre année scolaire"
                        )
                    })

        return data

class MatiereSerializer(serializers.ModelSerializer):
    etablissement = serializers.PrimaryKeyRelatedField(
        queryset=Etablissement.objects.all()
    )
    annee_scolaire = serializers.PrimaryKeyRelatedField(
        queryset=AnneeScolaire.objects.all(),
        required=False,
        allow_null=True,
    )
    annee_scolaire_nom = serializers.CharField(
        source='annee_scolaire.nom',
        read_only=True
    )

    classes_count = serializers.SerializerMethodField()
    classes_details = serializers.SerializerMethodField()

    class Meta:
        model = Matiere
        fields = [
            'id', 'nom', 'description',
            'etablissement', 'annee_scolaire', 'annee_scolaire_nom',
            'classes_count', 'classes_details',
            'created_at', 'updated_at',
        ]

    def get_classes_count(self, obj):
        return obj.classes.count()

    def get_classes_details(self, obj):
        return [
            {
                'id': c.id,
                'nom': c.nom,
                'niveau': c.niveau,
                'section': c.section,
                'annee_scolaire_nom': c.annee_scolaire.nom if c.annee_scolaire else None,
            }
            for c in obj.classes.all()
        ]

    def validate(self, data):
        nom = data.get('nom')
        etablissement = data.get('etablissement')
        annee_scolaire = data.get('annee_scolaire')

        # Vérifier que l'année appartient bien à l'établissement
        if etablissement and annee_scolaire:
            if annee_scolaire.etablissement_id != etablissement.id:
                raise serializers.ValidationError({
                    'annee_scolaire': "Cette année scolaire n'appartient pas à cet établissement"
                })

        # Vérifier l'unicité (nom + établissement + année)
        qs = Matiere.objects.filter(
            nom__iexact=nom,
            etablissement=etablissement,
            annee_scolaire=annee_scolaire,
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError({
                'nom': "Cette matière existe déjà pour cette année scolaire."
            })

        return data
    
class SalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salle
        fields = '__all__'

class CoursSerializer(serializers.ModelSerializer):

    classe_nom = serializers.CharField(
        source='classe.nom',
        read_only=True
    )

    professeur_nom = serializers.CharField(
        source='professeur.user.get_full_name',
        read_only=True
    )

    matiere_nom = serializers.CharField(
        source='matiere.nom',
        read_only=True
    )

    salle_nom = serializers.CharField(
        source='salle.nom',
        read_only=True
    )

    annee_nom = serializers.CharField(
        source='annee_scolaire.nom',
        read_only=True
    )

    date_specifique_formatted = serializers.SerializerMethodField()
    type_cours_display = serializers.SerializerMethodField()

    class Meta:
        model = Cours
        fields = '__all__'

    def get_date_specifique_formatted(self, obj):
        if obj.date_specifique:
            return obj.date_specifique.strftime('%d/%m/%Y')
        return None
    
    def get_type_cours_display(self, obj):
        return dict(Cours.TYPE_CHOICES).get(obj.type_cours, obj.type_cours)
    
    def validate(self, data):
        instance = self.instance
        type_cours = data.get('type_cours', instance.type_cours if instance else 'regulier')
        date_specifique = data.get('date_specifique', instance.date_specifique if instance else None)
        annee_scolaire = data.get('annee_scolaire', instance.annee_scolaire if instance else None)
        matiere = data.get('matiere', instance.matiere if instance else None)
        classe = data.get('classe', instance.classe if instance else None)
        professeur = data.get('professeur', instance.professeur if instance else None)

        if type_cours == 'specifique' and not date_specifique:
            raise serializers.ValidationError({
                'date_specifique': "Les cours spécifiques doivent avoir une date spécifique"
            })

        if date_specifique and annee_scolaire:
            if date_specifique < annee_scolaire.date_debut or date_specifique > annee_scolaire.date_fin:
                raise serializers.ValidationError({
                    'date_specifique': "La date spécifique doit être dans l'année scolaire"
                })

        if matiere and annee_scolaire and matiere.annee_scolaire_id:
            if matiere.annee_scolaire_id != annee_scolaire.id:
                raise serializers.ValidationError({
                    'matiere': (
                        f"La matière « {matiere.nom} » appartient à l'année "
                        f"« {matiere.annee_scolaire.nom} », pas à « {annee_scolaire.nom} »"
                    )
                })
                
        if classe and annee_scolaire and classe.annee_scolaire_id != annee_scolaire.id:
            raise serializers.ValidationError({
                'classe': (
                    f"La classe « {classe.nom} » appartient à l'année "
                    f"« {classe.annee_scolaire.nom} », pas à « {annee_scolaire.nom} »"
                )
            })

        if professeur and matiere:
            # Un prof doit enseigner cette matière (si la relation est renseignée)
            if professeur.matieres.exists() and not professeur.matieres.filter(id=matiere.id).exists():
                raise serializers.ValidationError({
                    'professeur': (
                        f"Le professeur « {professeur.user.get_full_name()} » "
                        f"n'enseigne pas la matière « {matiere.nom} »"
                    )
                })
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'telephone', 'user_type', 'profile']
    
    def get_profile(self, obj):
        if hasattr(obj, 'etablissement'):
            return EtablissementSerializer(obj.etablissement).data
        elif hasattr(obj, 'professeur'):
            return ProfesseurSerializer(obj.professeur).data
        elif hasattr(obj, 'eleve'):
            return EleveSerializer(obj.eleve).data
        elif hasattr(obj, 'parent'):
            return ParentSerializer(obj.parent).data
        return None

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, data):
        if 'username' not in data or not data['username']:
            data['username'] = data['email'] 
        return data
    
    def create(self, validated_data):
        if not validated_data.get('username'):
            validated_data['username'] = validated_data['email']
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class EtablissementSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    annees_scolaires = AnneeScolaireSerializer(many=True, read_only=True)
    classes = ClasseSerializer(many=True, read_only=True)
    
    # Champs supplémentaires pour la réponse
    distance = serializers.SerializerMethodField()
    has_coordinates = serializers.SerializerMethodField()
    
    class Meta:
        model = Etablissement
        fields = '__all__'
        extra_kwargs = {
            'nom': {'required': True},
            'type_etablissement': {'required': True},
            'latitude': {'required': False, 'allow_null': True},
            'longitude': {'required': False, 'allow_null': True},
            'coordinates_verified': {'read_only': True},
            'coordinates_updated_at': {'read_only': True},
        }
    
    def get_distance(self, obj):
        """Calcule la distance depuis la position de l'utilisateur"""
        request = self.context.get('request')
        if not request:
            return None
            
        user_lat = request.query_params.get('lat')
        user_lng = request.query_params.get('lng')
        
        if user_lat and user_lng and obj.latitude and obj.longitude:
            import math
            R = 6371  # Rayon de la Terre en km
            
            lat1 = float(user_lat)
            lng1 = float(user_lng)
            lat2 = float(obj.latitude)
            lng2 = float(obj.longitude)
            
            dlat = math.radians(lat2 - lat1)
            dlng = math.radians(lng2 - lng1)
            
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            
            return round(R * c, 2)
        
        return None
    
    def get_has_coordinates(self, obj):
        return obj.has_coordinates
    
    def validate(self, data):
        """Validation des données"""
        # Si des coordonnées sont fournies, vérifier qu'elles sont valides
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if latitude is not None and longitude is not None:
            # Vérifier que les coordonnées sont dans des plages valides
            if not (-90 <= float(latitude) <= 90):
                raise serializers.ValidationError({
                    'latitude': 'La latitude doit être comprise entre -90 et 90 degrés'
                })
            if not (-180 <= float(longitude) <= 180):
                raise serializers.ValidationError({
                    'longitude': 'La longitude doit être comprise entre -180 et 180 degrés'
                })
        
        return data
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['user_type'] = 'etablissement'
        
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        
        # Si des coordonnées sont fournies, marquer comme vérifiées
        if validated_data.get('latitude') and validated_data.get('longitude'):
            validated_data['coordinates_verified'] = True
            validated_data['coordinates_updated_at'] = timezone.now()
        
        return Etablissement.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if 'latitude' in validated_data or 'longitude' in validated_data:
            instance.coordinates_verified = True
            instance.coordinates_updated_at = timezone.now()
    
        if 'adresse' in validated_data and validated_data['adresse'] != instance.adresse:
            try:
                from .services.geocoding import GeocodingService
                coords = GeocodingService.geocode_address(validated_data['adresse'])
                if coords:
                    instance.latitude = coords['latitude']
                    instance.longitude = coords['longitude']
                    instance.coordinates_verified = True
                    instance.coordinates_updated_at = timezone.now()
            except ImportError:
                pass 

        instance.save()
        
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
        
        return instance

class ProfesseurSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    # Écriture
    classes = serializers.PrimaryKeyRelatedField(
        queryset=Classe.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

    matieres = serializers.PrimaryKeyRelatedField(
        queryset=Matiere.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

    # Lecture
    classes_details = serializers.SerializerMethodField()
    matieres_details = serializers.SerializerMethodField()
    annee_scolaire = serializers.SerializerMethodField()
    
    class Meta:
        model = Professeur
        fields = '__all__'
        extra_kwargs = {
            'matiere': {'required': True},
        }
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        classes = validated_data.pop('classes', [])
        matieres = validated_data.pop('matieres', [])

        user_data['user_type'] = 'professeur'

        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)

        user = user_serializer.save()

        professeur = Professeur.objects.create(
            user=user,
            **validated_data
        )

        # relation ManyToMany
        professeur.classes.set(classes)
        professeur.matieres.set(matieres)

        return professeur

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        classes = validated_data.pop('classes', None)
        matieres = validated_data.pop('matieres', None)

        if user_data:
            user = instance.user

            for attr, value in user_data.items():
                setattr(user, attr, value)

            user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if classes is not None:
            instance.classes.set(classes)

        if matieres is not None:
            instance.matieres.set(matieres)

        return instance

    def get_annee_scolaire(self, obj):
        """
        Récupère les années scolaires des classes du professeur
        """
        # Récupérer toutes les classes du professeur
        classes = obj.classes.all()
        
        if not classes.exists():
            return None
        
        # Récupérer les années scolaires uniques
        annees = classes.values_list('annee_scolaire__id', 'annee_scolaire__nom').distinct()
        
        # Si une seule classe, retourner juste l'ID
        if len(annees) == 1:
            return {
                "id": annees[0][0],
                "nom": annees[0][1]
            }

        return [
            {
                "id": annee_id,
                "nom": annee_nom
            }
            for annee_id, annee_nom in annees
        ]
    
    def get_classes_details(self, obj):
        return [
            {
                "id": c.id,
                "nom": c.nom
            }
            for c in obj.classes.all()
        ]

    def get_matieres_details(self, obj):
        return [
            {
                "id": m.id,
                "nom": m.nom
            }
            for m in obj.matieres.all()
        ]

class EleveSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    classe = serializers.PrimaryKeyRelatedField(queryset=Classe.objects.all(), required=True)
    annee_scolaire = serializers.SerializerMethodField()
    
    class Meta:
        model = Eleve
        fields = '__all__'
        extra_kwargs = {
            'classe': {'required': True},
        }

    def get_annee_scolaire(self, obj):
        # Accéder à l'année scolaire via la classe
        if obj.classe and obj.classe.annee_scolaire:
            return obj.classe.annee_scolaire.id
        return "Non assigné"
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['user_type'] = 'eleve'
        
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        
        return Eleve.objects.create(user=user, **validated_data)
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                if value is not None:
                    setattr(instance.user, attr, value)
            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class PeriodeSerializer(serializers.ModelSerializer):
    annee_scolaire = AnneeScolaireSerializer(read_only=True)
    annee_scolaire_id = serializers.PrimaryKeyRelatedField(
        queryset=AnneeScolaire.objects.all(),
        source='annee_scolaire',
        write_only=True
    )

    class Meta:
        model = Periode
        fields = ['id', 'nom', 'ordre', 'date_debut', 'date_fin', 'annee_scolaire', 'annee_scolaire_id', 'etablissement', 'created_at', 'updated_at']
        extra_kwargs = {'etablissement': {'read_only': True}}


class NoteSerializer(serializers.ModelSerializer):
    eleve_nom = serializers.CharField(source='eleve.user.get_full_name', read_only=True)
    eleve_classe = serializers.CharField(source='eleve.classe.nom', read_only=True)

    class Meta:
        model = Note
        fields = ['id', 'evaluation', 'eleve', 'eleve_nom', 'eleve_classe', 'note', 'appreciation', 'absent', 'created_at', 'updated_at']
        read_only_fields = ['id', 'evaluation', 'created_at', 'updated_at']


class EvaluationSerializer(serializers.ModelSerializer):
    matiere_nom = serializers.CharField(source='matiere.nom', read_only=True)
    classe_nom = serializers.CharField(source='classe.nom', read_only=True)
    professeur_nom = serializers.CharField(source='professeur.user.get_full_name', read_only=True)
    periode_nom = serializers.CharField(source='periode.nom', read_only=True)
    notes = NoteSerializer(many=True, read_only=True)
    notes_count = serializers.SerializerMethodField()
    moyenne_classe = serializers.SerializerMethodField()

    class Meta:
        model = Evaluation
        fields = '__all__'
        extra_kwargs = {
            'etablissement': {'read_only': True},
            'statut': {'read_only': False},
        }

    def get_notes_count(self, obj):
        return obj.notes.count()

    def get_moyenne_classe(self, obj):
        notes = obj.notes.filter(absent=False, note__isnull=False)
        if notes.exists():
            return round(notes.aggregate(Avg('note'))['note__avg'], 2)
        return None


class EvaluationDetailSerializer(EvaluationSerializer):
    """Serializer pour le détail avec les notes complètes"""
    notes = NoteSerializer(many=True, read_only=True)

class ParentSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    enfants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Eleve.objects.all(),
        required=False
    )
    
    class Meta:
        model = Parent
        fields = '__all__'
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        enfants = validated_data.pop('enfants', [])
        user_data['user_type'] = 'parent'
        
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        
        parent = Parent.objects.create(user=user, **validated_data)
        parent.enfants.set(enfants)
        return parent