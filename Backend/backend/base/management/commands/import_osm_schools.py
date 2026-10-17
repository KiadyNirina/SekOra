import requests
import time
from django.core.management.base import BaseCommand
from base.models import EcoleOSM


OVERPASS_SERVERS = [
    'https://overpass.kumi.systems/api/interpreter',
    'https://overpass-api.de/api/interpreter',
    'https://overpass.private.coffee/api/interpreter',
]

def detect_type(tags):
    """
    Détecte le type d'école à partir des tags OSM.
    Logique basée sur le nom en priorité, puis amenity, puis ISCED.
    """
    name = tags.get('name', '').lower()

    # 1. École supérieure / institut supérieur → university
    if any(w in name for w in [
        'école sup', 'ecole sup', 'institut sup',
        'université', 'university', 'faculté', 'faculty',
        'école normale sup', 'ecole normale sup',
    ]):
        return 'university'
    
    # 2. Lycée → lycee
    if any(w in name for w in ['lycée', 'lycee', 'high school']):
        return 'lycee'

    # 3. Collège → college
    if any(w in name for w in ['collège', 'college', 'ceg', 'middle school']):
        return 'college'

    # 4. Maternelle / crèche / jardin d'enfants → kindergarten
    if any(w in name for w in ['maternelle', 'kindergarten', 'crèche', 'creche', 'jardin d\'enfant']):
        return 'kindergarten'

    # 5. École (primaire) → school
    if any(w in name for w in ['école', 'ecole', 'epp', 'primary', 'primaire']):
        return 'school'

    # 6. Tag amenity OSM (si le nom n'a rien donné)
    amenity = tags.get('amenity', '').lower()
    if amenity in ('school', 'college', 'university', 'kindergarten'):
        return amenity

    # 7. ISCED (classification UNESCO)
    isced = tags.get('isced:level', '')
    if isced:
        if '5' in isced or '6' in isced or '7' in isced or '8' in isced:
            return 'university'
        if '1' in isced or '2' in isced or '3' in isced:
            return 'school'

    # 8. Défaut
    return 'school'

class Command(BaseCommand):
    help = "Importe les écoles depuis OpenStreetMap (Overpass API)"

    def add_arguments(self, parser):
        parser.add_argument('--lat', type=float, required=True)
        parser.add_argument('--lng', type=float, required=True)
        parser.add_argument('--radius', type=int, default=5000)

    def handle(self, *args, **options):
        lat = options['lat']
        lng = options['lng']
        radius = options['radius']

        self.stdout.write(f"🌐 Import OSM autour de ({lat}, {lng}) rayon {radius}m")

        query = f"""
        [out:json][timeout:180];
        (
          nwr(around:{radius},{lat},{lng})[amenity=school];
          nwr(around:{radius},{lat},{lng})[amenity=college];
          nwr(around:{radius},{lat},{lng})[amenity=university];
        );
        out center;
        """

        headers = {
            'User-Agent': 'EbossSchoolMap/1.0 (import script)',
            'Accept': 'application/json',
        }

        data = None
        for server in OVERPASS_SERVERS:
            try:
                self.stdout.write(f"🌐 Essai sur {server}...")
                response = requests.post(
                    server,
                    data={'data': query},
                    headers=headers,
                    timeout=200
                )
                if not response.text.strip().startswith('{'):
                    self.stderr.write(f"⚠️ {server} → HTTP {response.status_code}, on essaie le suivant")
                    continue
                data = response.json()
                self.stdout.write(f"✅ Succès sur {server}")
                break
            except Exception as e:
                self.stderr.write(f"⚠️ {server} → erreur: {e}")
                continue

        if not data:
            self.stderr.write("❌ Tous les serveurs Overpass ont échoué")
            return

        elements = data.get('elements', [])
        self.stdout.write(f"📦 {len(elements)} éléments reçus")

        created = 0
        updated = 0
        skipped = 0

        for el in elements:
            lat_val = el.get('lat') or el.get('center', {}).get('lat')
            lng_val = el.get('lon') or el.get('center', {}).get('lon')

            if not lat_val or not lng_val:
                skipped += 1
                continue

            tags = el.get('tags', {})
            osm_id = f"osm_{el['type']}_{el['id']}"

            defaults = {
                'nom': tags.get('name', ''),
                'adresse': (
                    tags.get('addr:full')
                    or tags.get('addr:street')
                    or tags.get('addr:suburb')
                    or tags.get('addr:city')
                    or ''
                ),
                'latitude': lat_val,
                'longitude': lng_val,
                'type_ecole': detect_type(tags),
                'source': 'osm',
            }

            obj, is_created = EcoleOSM.objects.update_or_create(
                osm_id=osm_id,
                defaults=defaults
            )

            if is_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ Import terminé : {created} créées, {updated} mises à jour, {skipped} ignorées"
        ))
        self.stdout.write(f"📊 Total en BDD : {EcoleOSM.objects.count()} écoles OSM")