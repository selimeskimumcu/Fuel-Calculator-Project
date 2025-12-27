let map = L.map('map').setView([41.0082, 28.9784], 11); // İstanbul
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
}).addTo(map);

let startMarker = null;
let endMarker = null;
let startCoord = null; // [lon, lat]
let endCoord = null;

let lastRouteSummery = null;

function setMarker(latlng) {
  if (!startMarker) {
    startMarker = L.marker(latlng).addTo(map).bindPopup("Başlangıç").openPopup();
    startCoord = [latlng.lng, latlng.lat];
    return;
  }
  if (!endMarker) {
    endMarker = L.marker(latlng).addTo(map).bindPopup("Varış").openPopup();
    endCoord = [latlng.lng, latlng.lat];
    return;
  }
}

map.on('click', (e) => setMarker(e.latlng));

document.getElementById("btnClear").onclick = () => {
  if (startMarker) map.removeLayer(startMarker);
  if (endMarker) map.removeLayer(endMarker);
  startMarker = endMarker = null;
  startCoord = endCoord = null;
  lastRouteSummery = null;
  document.getElementById("routeInfo").innerText = "";
  document.getElementById("result").innerHTML = "";
};

document.getElementById("btnRoute").onclick = async () => {
  if (!startCoord || !endCoord) {
    alert("Haritadan önce başlangıç ve varış noktası seç.");
    return;
  }

  const res = await fetch("/api/route", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ start_coord: startCoord, end_coord: endCoord })
  });

  const data = await res.json();
  if (!res.ok) {
    alert(data.error || "Rota hatası");
    return;
  }

  lastRouteSummery = data.route_summery;

  document.getElementById("routeInfo").innerText =
    `Mesafe: ${data.route_summery.total_distance_km} km | Şehir içi: %${data.route_summery.urban_percent} | Şehir dışı: %${data.route_summery.interurban_percent}`;
};

document.getElementById("btnCalc").onclick = async () => {
  if (!lastRouteSummery) {
    alert("Önce 'Rota Hesapla' yap.");
    return;
  }

  const make = document.getElementById("make").value.trim();
  const model = document.getElementById("model").value.trim();
  const year = document.getElementById("year").value.trim();
  const fuelType = document.getElementById("fuelType").value;

  if (!make || !model || !year) {
    alert("Make/Model/Year boş olamaz.");
    return;
  }

  // start_district şu an route_data.json'dan gelmiyor.
  // Şimdilik kullanıcıdan adres/district seçimi eklenirse buraya koyacağız.
  // Hızlı demo için: İstanbul ilçesini kullanıcıdan ayrıca alabilirsiniz (ek input).
  // Şimdilik backend start_address veya start_district istiyor; burada basit geçelim:
  const start_district = prompt("Başlangıç ilçesi (örn: FATIH / KADIKOY / CEKMEKOY):");
  if (!start_district) return;

  const payload = {
    route_summery: lastRouteSummery,
    start_district: start_district,
    vehicle: { make, model, year: parseInt(year, 10) },
    fuel_type: fuelType
  };

  const res = await fetch("/api/calculate", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(payload)
  });

  const data = await res.json();
  if (!res.ok) {
    alert(data.error || "Hesaplama hatası");
    return;
  }

  document.getElementById("result").innerHTML = `
    <h3>Sonuç</h3>
    <div>Toplam Yakıt: <b>${data.fuel_used?.toFixed ? data.fuel_used.toFixed(2) : data.fuel_used}</b> L</div>
    <div>Toplam Maliyet: <b>${data.total_cost?.toFixed ? data.total_cost.toFixed(2) : data.total_cost}</b> TL</div>
    <div>Karma Tüketim: <b>${data.mixed_consumption?.toFixed ? data.mixed_consumption.toFixed(2) : data.mixed_consumption}</b> L/100km</div>
    <div class="muted">İlçe: ${data.district} | Yakıt: ${data.fuel_type}</div>
  `;
};
