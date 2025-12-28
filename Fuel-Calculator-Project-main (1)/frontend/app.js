// Harita oluştur
const map = L.map('map').setView([39.0, 35.0], 6);

// Harita katmanı
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
}).addTo(map);

let startMarker = null;
let endMarker = null;

// Haritaya tıklama
map.on('click', function (e) {
    if (!startMarker) {
        startMarker = L.marker(e.latlng).addTo(map);
        document.getElementById("start").value =
            e.latlng.lat.toFixed(5) + ", " + e.latlng.lng.toFixed(5);
    } else if (!endMarker) {
        endMarker = L.marker(e.latlng).addTo(map);
        document.getElementById("end").value =
            e.latlng.lat.toFixed(5) + ", " + e.latlng.lng.toFixed(5);
    }
});

// Hesapla butonu
function calculate() {
    console.log("Butona basıldı");

    const startPoint = startMarker ? startMarker.getLatLng() : null;
    const endPoint = endMarker ? endMarker.getLatLng() : null;

    if (!startPoint || !endPoint) {
        alert("Lütfen haritadan başlangıç ve varış seç");
        return;
    }

    const data = {
        start: { lat: startPoint.lat, lng: startPoint.lng },
        end: { lat: endPoint.lat, lng: endPoint.lng },
        brand: document.getElementById("brand").value,
        model: document.getElementById("model").value,
        year: document.getElementById("year").value,
        fuel: document.getElementById("fuel").value
    };

    console.log("Gönderilen veri:", data);

    fetch("http://127.0.0.1:5000/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
        console.log("Backend cevabı:", result);
        document.getElementById("result").innerText =
            "Sonuç: " + JSON.stringify(result);
    })
    .catch(err => {
        console.error(err);
        alert("Backend hatası");
    });
}
