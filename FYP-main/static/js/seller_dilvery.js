const citiesEl = document.getElementById('delivery-cities-data');
let cities = {};
try {
  cities = citiesEl ? JSON.parse(citiesEl.textContent || '{}') : {};
} catch (e) {
  cities = {};
}

let map, marker, circle;

function initMap() {
  map = L.map('map').setView([31.0, 70.0], 6);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: 'CartoDB',
  }).addTo(map);
}

function updateAll() {
  const city = document.getElementById('baseCity').value;
  const radius = document.getElementById('radiusSlider').value;
  document.getElementById('radiusVal').textContent = radius;

  if (!city) {
    document.getElementById('cityTags').innerHTML = '<span class="text-gray-500 text-xs">Select city</span>';
    if (marker) map.removeLayer(marker);
    if (circle) map.removeLayer(circle);
    return;
  }

  const pos = cities[city];
  const latlng = [pos.lat, pos.lng];

  if (!marker) {
    marker = L.marker(latlng).addTo(map).bindPopup(city).openPopup();
  } else {
    marker.setLatLng(latlng);
  }

  if (!circle) {
    circle = L.circle(latlng, { radius: radius * 1000, color: '#1e40af', weight: 3, fillOpacity: 0.15 }).addTo(map);
  } else {
    circle.setLatLng(latlng).setRadius(radius * 1000);
  }

  map.setView(latlng, 8);

  // Covered cities
  const covered = Object.keys(cities).filter(c => {
    const d = map.distance(latlng, [cities[c].lat, cities[c].lng]) / 1000;
    return d <= radius;
  });

  const tags = document.getElementById('cityTags');
  tags.innerHTML = '';
  covered.forEach(c => {
    const span = document.createElement('span');
    span.className = 'city-tag';
    span.textContent = c;
    tags.appendChild(span);
  });
}

function saveSettings() {
  const city = document.getElementById('baseCity').value;
  const radius = document.getElementById('radiusSlider').value;
  if (!city) return alert("Select city first!");

  localStorage.setItem('deliveryCity', city);
  localStorage.setItem('deliveryRadius', radius);

  document.getElementById('savedStatus').classList.remove('hidden');
  setTimeout(() => document.getElementById('savedStatus').classList.add('hidden'), 2000);
}

// Events
const baseCityEl = document.getElementById('baseCity');
const radiusSliderEl = document.getElementById('radiusSlider');
if (baseCityEl) baseCityEl.addEventListener('change', updateAll);
if (radiusSliderEl) radiusSliderEl.addEventListener('input', updateAll);

// Load saved
window.onload = () => {
  const mapEl = document.getElementById('map');
  if (!mapEl) return;
  initMap();

  const city = localStorage.getItem('deliveryCity');
  const radius = localStorage.getItem('deliveryRadius');
  if (city && baseCityEl) {
    baseCityEl.value = city;
    if (radius && radiusSliderEl) radiusSliderEl.value = radius;
    updateAll();
  }
};