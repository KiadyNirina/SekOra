from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('etablissement', 'Établissement'),
        ('professeur', 'Professeur'),
        ('eleve', 'Élève'),
        ('parent', 'Parent'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    
    # Champs communs
    adresse = models.TextField(blank=True, null=True)

    profile_image = models.ImageField(
        upload_to='profiles/', 
        blank=True, 
        null=True,
        help_text="Photo de profil de l'utilisateur"
    )
    
    def clean(self):
        if self.user_type == 'etablissement' and not hasattr(self, 'etablissement'):
            if not self.pk: 
                return 
            raise ValidationError("Les établissements doivent avoir un profil établissement complété")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class AnneeScolaire(models.Model):
    etablissement = models.ForeignKey(
        'Etablissement',
        on_delete=models.CASCADE,
        related_name='annees_scolaires',
    )
    nom = models.CharField(max_length=50)
    date_debut = models.DateField()
    date_fin = models.DateField()
    est_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_debut']
        verbose_name = "Année scolaire"
        verbose_name_plural = "Années scolaires"
        unique_together = ('etablissement', 'nom')

class Etablissement(models.Model):
    TYPE_CHOICES = (
        ('ecole', 'École primaire'),
        ('college', 'Collège'),
        ('lycee', 'Lycée'),
        ('universite', 'Université'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='etablissement')
    type_etablissement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    nom = models.CharField(max_length=255)
    adresse = models.TextField()
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=8, 
        null=True, 
        blank=True,
        help_text="Latitude de l'établissement"
    )
    longitude = models.DecimalField(
        max_digits=11, 
        decimal_places=8, 
        null=True, 
        blank=True,
        help_text="Longitude de l'établissement"
    )
    # Champ pour stocker si les coordonnées ont été vérifiées
    coordinates_verified = models.BooleanField(
        default=False,
        help_text="Indique si les coordonnées ont été vérifiées"
    )
    
    # Date de dernière mise à jour des coordonnées
    coordinates_updated_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Date de dernière mise à jour des coordonnées"
    )
    
    def __str__(self):
        return self.nom
    
    @property
    def coordinates(self):
        """Retourne les coordonnées sous forme de tuple"""
        if self.latitude and self.longitude:
            return (float(self.latitude), float(self.longitude))
        return None
    
    @property
    def has_coordinates(self):
        """Vérifie si l'établissement a des coordonnées"""
        return self.latitude is not None and self.longitude is not None
    
    def update_coordinates(self, latitude, longitude, verified=True):
        """Met à jour les coordonnées"""
        self.latitude = latitude
        self.longitude = longitude
        self.coordinates_verified = verified
        self.coordinates_updated_at = timezone.now()
        self.save()
    
class Matiere(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    etablissement = models.ForeignKey(
        Etablissement,
        on_delete=models.CASCADE,
        related_name='matieres'
    )

    def __str__(self):
        return self.nom

    class Meta:
        unique_together = ('nom', 'etablissement')
        verbose_name = "Matière"
        verbose_name_plural = "Matières"

class Classe(models.Model):
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name='classes')
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, related_name='classes')
    nom = models.CharField(max_length=100)  # Ex: "CE1 A" ou "Terminale S"
    niveau = models.CharField(max_length=50)  # Ex: "CE1", "Terminale", etc.
    section = models.CharField(max_length=10, blank=True, null=True)  # Ex: "A", "B", "S", "ES", etc.
    professeur_principal = models.ForeignKey('Professeur', on_delete=models.SET_NULL, null=True, blank=True)
    matieres = models.ManyToManyField(Matiere,blank=True,related_name='classes')
    
    def __str__(self):
        section = f" {self.section}" if self.section else ""
        return f"{self.niveau}{section} - {self.annee_scolaire.nom}"
    
    class Meta:
        unique_together = ('etablissement', 'annee_scolaire', 'nom', 'niveau', 'section')
        verbose_name_plural = "Classes"

class Professeur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professeur')
    etablissement = models.ForeignKey(Etablissement, on_delete=models.SET_NULL, null=True, blank=True, related_name='professeurs')
    matieres = models.ManyToManyField(Matiere, blank=True, related_name='professeurs')
    classes = models.ManyToManyField(Classe, blank=True, related_name='professeurs')
    
    def __str__(self):
        return self.user.get_full_name()

class Salle(models.Model):
    etablissement = models.ForeignKey(
        Etablissement,
        on_delete=models.CASCADE,
        related_name='salles'
    )
    nom = models.CharField(max_length=50)  # Salle 1, Laboratoire, etc.
    capacite = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nom
    
class Cours(models.Model):
    TYPE_CHOICES = (
        ('regulier', 'Régulier'),
        ('specifique', 'Spécifique'),
        ('exceptionnel', 'Exceptionnel'),
    )

    JOURS_CHOICES = (
        ('lundi', 'Lundi'),
        ('mardi', 'Mardi'),
        ('mercredi', 'Mercredi'),
        ('jeudi', 'Jeudi'),
        ('vendredi', 'Vendredi'),
        ('samedi', 'Samedi'),
    )

    etablissement = models.ForeignKey(
        Etablissement,
        on_delete=models.CASCADE,
        related_name='cours'
    )

    classe = models.ForeignKey(
        Classe,
        on_delete=models.CASCADE,
        related_name='cours'
    )

    professeur = models.ForeignKey(
        Professeur,
        on_delete=models.CASCADE,
        related_name='cours'
    )

    matiere = models.ForeignKey(
        Matiere,
        on_delete=models.CASCADE,
        related_name='cours'
    )

    salle = models.ForeignKey(
        Salle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cours'
    )

    jour = models.CharField(
        max_length=10,
        choices=JOURS_CHOICES
    )

    heure_debut = models.TimeField()
    heure_fin = models.TimeField()

    annee_scolaire = models.ForeignKey(
        AnneeScolaire,
        on_delete=models.CASCADE,
        related_name='cours'
    )

    date_specifique = models.DateField(
        null=True, 
        blank=True,
        help_text="Date spécifique pour ce cours (ex: cours exceptionnel)"
    )

    type_cours = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='regulier',
        help_text="Régulier (chaque semaine) ou Spécifique (date unique)"
    )

    def __str__(self):
        date_info = f" - {self.date_specifique}" if self.date_specifique else ""
        type_info = f" [{self.type_cours}]"
        return (
            f"{self.matiere.nom} - "
            f"{self.classe.nom} - "
            f"{self.jour}{date_info}{type_info}"
        )

    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"

    def save(self, *args, **kwargs):
        # Auto-déterminer le type si non spécifié
        if self.date_specifique and self.type_cours == 'regulier':
            self.type_cours = 'specifique'
        super().save(*args, **kwargs)

class Periode(models.Model):
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name='periodes')
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, related_name='periodes')
    nom = models.CharField(max_length=50)  # ex: "1er Trimestre", "Semestre 1"
    ordre = models.PositiveSmallIntegerField()  # 1, 2, 3...
    date_debut = models.DateField()
    date_fin = models.DateField()

    class Meta:
        unique_together = ('etablissement', 'annee_scolaire', 'nom')
        ordering = ['annee_scolaire', 'ordre']

    def __str__(self):
        return f"{self.nom} ({self.annee_scolaire.nom})"

class Evaluation(models.Model):
    TYPE_CHOICES = (
        ('controle', 'Contrôle'),
        ('examen', 'Examen'),
        ('devoir', 'Devoir maison'),
        ('projet', 'Projet'),
        ('autre', 'Autre'),
    )
    STATUT_CHOICES = (
        ('brouillon', 'Brouillon'),
        ('publie', 'Publié'),
    )

    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name='evaluations')
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='evaluations')
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='evaluations')
    professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE, related_name='evaluations')
    periode = models.ForeignKey(Periode, on_delete=models.SET_NULL, null=True, blank=True, related_name='evaluations')
    nom = models.CharField(max_length=255)  # ex: "Contrôle de mathématiques n°1"
    date = models.DateField()
    coefficient = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='controle')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    description = models.TextField(blank=True, null=True)
    bareme = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Note maximale possible (ex: 20)")

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.nom} - {self.classe.nom} ({self.date})"

class Eleve(models.Model):
    STATUS_CHOICES = (
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('suspendu', 'Suspendu'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='eleve')
    etablissement = models.ForeignKey(Etablissement, on_delete=models.SET_NULL, null=True, blank=True)
    classe = models.ForeignKey(Classe, on_delete=models.SET_NULL, null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='actif')
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.classe.nom if self.classe else 'Non assigné'})"

class Note(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='notes')
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name='notes')
    note = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # ex: 15.5
    appreciation = models.TextField(blank=True, null=True)
    absent = models.BooleanField(default=False)

    class Meta:
        unique_together = ('evaluation', 'eleve')  # un élève n'a qu'une note par évaluation

    def __str__(self):
        return f"{self.eleve} - {self.evaluation.nom} : {self.note or 'Absent'}"

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent')
    enfants = models.ManyToManyField(Eleve, blank=True)
    
    def __str__(self):
        return self.user.get_full_name()
    
class EcoleOSM(models.Model):
    """
    Écoles importées depuis OpenStreetMap (Overpass API).
    Licence ODbL — crédit OpenStreetMap obligatoire.
    """
    osm_id = models.CharField(max_length=50, unique=True, db_index=True)
    nom = models.CharField(max_length=255, blank=True)
    adresse = models.CharField(max_length=500, blank=True)
    latitude = models.FloatField(db_index=True)
    longitude = models.FloatField(db_index=True)
    type_ecole = models.CharField(max_length=50, blank=True)  # school, college, university
    source = models.CharField(max_length=20, default='osm')

    # Métadonnées
    imported_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "École OSM"
        verbose_name_plural = "Écoles OSM"
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        return self.nom or f"École OSM #{self.osm_id}"