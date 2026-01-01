let map = L.map('map').setView([41.0082, 28.9784], 11); // İstanbul
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
}).addTo(map);

let startMarker = null;
let endMarker = null;
let startCoord = null; // [lon, lat]
let endCoord = null;

let lastRouteSummery = null;

// ✅ /api/route'tan saklanacak bilgiler
let savedStartAddress = "";
let savedStartDistrict = "";

// route_data.json cache
let routeDataCache = null;

async function getRouteData(forceReload = false) {
  if (!forceReload && routeDataCache) return routeDataCache;

  try {
    const res = await fetch("/route_data.json", { cache: "no-store" });
    if (!res.ok) return null;
    routeDataCache = await res.json();
    return routeDataCache;
  } catch (e) {
    console.warn("route_data.json okunamadı:", e);
    return null;
  }
}

const ISTANBUL_DISTRICTS = [
  "ADALAR","ARNAVUTKÖY","ATAŞEHİR","AVCILAR","BAĞCILAR","BAHÇELİEVLER","BAKIRKÖY",
  "BAŞAKŞEHİR","BAYRAMPAŞA","BEŞİKTAŞ","BEYKOZ","BEYLİKDÜZÜ","BEYOĞLU",
  "BÜYÜKÇEKMECE","ÇATALCA","ÇEKMEKÖY","ESENLER","ESENYURT","EYÜPSULTAN",
  "FATİH","GAZİOSMANPAŞA","GÜNGÖREN","KADIKÖY","KAĞITHANE","KARTAL",
  "KÜÇÜKÇEKMECE","MALTEPE","PENDİK","SANCAKTEPE","SARIYER","SİLİVRİ",
  "SULTANBEYLİ","SULTANGAZİ","ŞİLE","ŞİŞLİ","TUZLA","ÜMRANİYE","ÜSKÜDAR",
  "ZEYTİNBURNU"
];

function deriveDistrictFromAddress(address) {
  if (!address || typeof address !== "string") return "";
  const up = address.toLocaleUpperCase("tr-TR");
  for (const d of ISTANBUL_DISTRICTS) {
    if (up.includes(d)) return d;
  }
  const first = address.split(",")[0]?.trim();
  return first ? first.toLocaleUpperCase("tr-TR") : "";
}

// fuel_type normalize: backend sadece benzin/mazot/lpg kabul ediyor
function normalizeFuelType(raw) {
  const v = (raw || "").toString().trim().toLowerCase();
  const map = {
    "benzin": "benzin",
    "gasoline": "benzin",
    "petrol": "benzin",
    "mazot": "mazot",
    "diesel": "mazot",
    "lpg": "lpg",
    "autogas": "lpg",
  };
  return map[v] || v;
}

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

  savedStartAddress = "";
  savedStartDistrict = "";
  routeDataCache = null;

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

  // ✅ artık backend start_district de döndürüyor
  savedStartAddress = (data.start_address || "").trim();
  savedStartDistrict = (data.start_district || "").trim().toLocaleUpperCase("tr-TR");

  // fallback: response boşsa route_data.json’dan çek
  if (!savedStartDistrict || !savedStartAddress) {
    routeDataCache = null;
    const rd = await getRouteData(true);
    if (rd) {
      savedStartAddress = savedStartAddress || (rd.start_address || "").trim();
      savedStartDistrict = savedStartDistrict || (rd.start_district || "").trim().toLocaleUpperCase("tr-TR");
      if (!lastRouteSummery && rd.route_summery) lastRouteSummery = rd.route_summery;
    }
  }

  // son fallback: address içinden çıkar
  if (!savedStartDistrict && savedStartAddress) {
    savedStartDistrict = deriveDistrictFromAddress(savedStartAddress);
  }

  document.getElementById("routeInfo").innerText =
    `Mesafe: ${data.route_summery.total_distance_km} km | Şehir içi: %${data.route_summery.urban_percent} | Şehir dışı: %${data.route_summery.interurban_percent}`;
};

document.getElementById("btnCalc").onclick = async () => {
  const make = document.getElementById("make").value.trim();
  const model = document.getElementById("model").value.trim();
  const year = document.getElementById("year").value.trim();
  const fuelRaw = document.getElementById("fuelType").value;

  if (!make || !model || !year) {
    alert("Make/Model/Year boş olamaz.");
    return;
  }

  const fuelType = normalizeFuelType(fuelRaw);

  // ✅ state kaybolduysa route_data.json’dan geri yükle
  const rd = await getRouteData(true);
  if (rd) {
    if (!lastRouteSummery && rd.route_summery) lastRouteSummery = rd.route_summery;
    if (!savedStartAddress && rd.start_address) savedStartAddress = (rd.start_address || "").trim();
    if (!savedStartDistrict && rd.start_district) savedStartDistrict = (rd.start_district || "").trim().toLocaleUpperCase("tr-TR");
  }

  // route_summery kontrol
  if (!lastRouteSummery) {
    alert("Önce 'Rota Hesapla' yap.");
    return;
  }

  if (
    lastRouteSummery.total_distance_km == null ||
    lastRouteSummery.urban_percent == null ||
    lastRouteSummery.interurban_percent == null
  ) {
    alert("route_summery eksik: total_distance_km / urban_percent / interurban_percent.");
    return;
  }

  // district son fallback
  if (!savedStartDistrict && savedStartAddress) {
    savedStartDistrict = deriveDistrictFromAddress(savedStartAddress);
  }

  if (!savedStartDistrict && !savedStartAddress) {
    alert("Başlangıç adresi/ilçesi yok. Önce 'Rota Hesapla' yap (route_data.json oluşsun).");
    return;
  }

  // İstersen burada İstanbul ilçesi değilse uyar:
  // if (savedStartDistrict && !ISTANBUL_DISTRICTS.includes(savedStartDistrict)) {
  //   alert(`İstanbul ilçesi değil gibi görünüyor: '${savedStartDistrict}'. Lütfen İstanbul içinden başlangıç seç.`);
  //   return;
  // }

  const payload = {
    route_summery: lastRouteSummery,
    start_district: savedStartDistrict || "",
    start_address: savedStartAddress || "",
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
    alert(data.error || "calculation error");
    return;
  }

  document.getElementById("result").innerHTML = `
    <h3>Result</h3>
    <div>Total Fuel: <b>${data.fuel_used?.toFixed ? data.fuel_used.toFixed(2) : data.fuel_used}</b> L</div>
    <div>Total Cost: <b>${data.total_cost?.toFixed ? data.total_cost.toFixed(2) : data.total_cost}</b> TL</div>
    <div>Mixed Consumption: <b>${data.mixed_consumption?.toFixed ? data.mixed_consumption.toFixed(2) : data.mixed_consumption}</b> L/100km</div>
    <div class="muted">İlçe: ${data.district} | Yakıt: ${data.fuel_type}</div>
  `;
};
