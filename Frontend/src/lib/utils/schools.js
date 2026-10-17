// Distance Haversine en mètres
export function distanceMeters(lat1, lng1, lat2, lng2) {
  const R = 6371000;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) *
    Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

// Normalise un nom pour comparer (minuscules, sans accents, sans espaces multiples)
function normalizeName(name = '') {
  return name
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9 ]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

// Vérifie si une école Google est déjà dans la liste "inscrite"
export function isDuplicate(googleSchool, registeredSchools) {
  return registeredSchools.some(reg => {
    const dist = distanceMeters(
      googleSchool.lat, googleSchool.lng,
      reg.lat, reg.lng
    );
    if (dist < 50) return true; // même endroit quasi exact

    // Si proche ET même nom → doublon
    if (dist < 200) {
      const a = normalizeName(googleSchool.name);
      const b = normalizeName(reg.name);
      if (a && b && (a.includes(b) || b.includes(a))) return true;
    }
    return false;
  });
}