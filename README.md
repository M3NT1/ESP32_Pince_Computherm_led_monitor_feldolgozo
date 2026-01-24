# 🔴 ESP32-CAM LED Monitor - Home Assistant Integráció

![ESP32-CAM](https://img.shields.io/badge/ESP32--CAM-AI--Thinker-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-MQTT-orange)

Computherm fűtésszabályozó LED állapotfigyelő rendszer Home Assistant integrációval.

## 📋 Funkciók

- ✅ **Webes konfiguráló felület** - LED területek egyszerű kijelölése egérrel
- ✅ **4 fűtési zóna monitorozása** - Testreszabható elnevezésekkel
- ✅ **Valós idejű LED detektálás** - OpenCV-alapú képfeldolgozás
- ✅ **MQTT integráció** - Automatikus Home Assistant device discovery
- ✅ **Állapot előzmények** - Nyomon követhető mikor volt be/kikapcsolva minden zóna
- ✅ **Élő monitoring** - Vizuális visszajelzés a webes felületen
- ✅ **Automatikus újracsatlakozás** - WiFi és MQTT kapcsolat kezelése

## 🏗️ Architektúra

```
┌─────────────────┐      HTTP       ┌──────────────────┐
│   ESP32-CAM     │◄────────────────│  Python Flask    │
│  (streaming)    │                 │   Feldolgozó     │
└─────────────────┘                 └────────┬─────────┘
                                             │
                                          MQTT │
                                             │
                                    ┌────────▼─────────┐
                                    │ Home Assistant   │
                                    │  + Mosquitto     │
                                    └──────────────────┘
```

## 🚀 Telepítés

### 🍓 Raspberry Pi 4 (ajánlott - Home Assistant környezethez)

Ha Raspberry Pi 4-en fut a Home Assistant:

**Lásd a részletes útmutatót:** [RASPBERRY_PI_INSTALL.md](RASPBERRY_PI_INSTALL.md)

**Gyors telepítés:**
```bash
# Fájlok másolása Raspberry Pi-re
scp -r Home_assistant_kiegeszito_feldolgozo pi@[RASPBERRY_PI_IP]:/home/pi/

# SSH csatlakozás
ssh pi@[RASPBERRY_PI_IP]

# Telepítő futtatása
cd /home/pi/Home_assistant_kiegeszito_feldolgozo
chmod +x install_rpi.sh
sudo ./install_rpi.sh
```

A telepítő automatikusan:
- ✅ Telepíti az összes függőséget
- ✅ Létrehoz egy systemd service-t
- ✅ Beállítja az automatikus indítást
- ✅ Optimalizálja Raspberry Pi-re

---

### 💻 Kézi telepítés (Mac/Linux/Windows)

### 1. Előfeltételek

```bash
# Python 3.8 vagy újabb
python3 --version

# pip frissítése
pip3 install --upgrade pip
```

### 2. Python függőségek telepítése

```bash
cd Home_assistant_kiegeszito_feldolgozo
pip3 install -r requirements.txt
```

### 3. Home Assistant MQTT Broker beállítása

#### Mosquitto Broker telepítése (Raspberry Pi-n)

**Home Assistant Supervisor módban:**
1. Settings → Add-ons → Add-on Store
2. Keress rá: "Mosquitto broker"
3. Telepítés → Start → Auto-start bekapcsolása

**Kézi telepítés (Linux/Raspberry Pi):**
```bash
sudo apt-get update
sudo apt-get install mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

#### Home Assistant configuration.yaml

```yaml
mqtt:
  broker: localhost
  port: 1883
  discovery: true
  discovery_prefix: homeassistant
```

Újraindítás után:
```bash
ha core restart
```

### 4. ESP32-CAM feltöltése

1. Nyisd meg az Arduino IDE-t
2. Töltsd fel az ESP32-CAM kódot (lásd: `esp32cam_streaming.ino`)
3. Jegyezd meg az ESP32-CAM IP címét a Serial Monitor-ból

## ⚙️ Beállítás és Használat

### 1. Alkalmazás indítása

```bash
python3 app.py
```

A webes felület elérhető: **http://localhost:5000**

### 2. Alapbeállítások

A **⚙️ Beállítás** fülön:

- **ESP32-CAM IP cím**: Az ESP32-CAM IP címe (pl: `http://192.168.1.100`)
- **MQTT Broker**: A Home Assistant IP címe vagy `localhost` (ha ugyanazon a gépen fut)
- **MQTT Port**: Alapértelmezett `1883`
- **MQTT Felhasználó/Jelszó**: Ha be van állítva authentication

Kattints a **💾 Konfiguráció mentése** gombra.

### 3. LED Zónák kijelölése

A **📍 Zónák** fülön:

1. Kattints a **📷 Kép betöltése** gombra
2. Jelöld ki az egérrel a LED területeket (bal gomb lenyomva + húzás)
3. Add meg minden zónának a nevét (pl: Nappali, Háló, Gyerekszoba, Fürdő)
4. Finomhangolható a **Küszöb** érték (fényerősség érzékenység, alapértelmezett: 30)
5. Kattints a **💾 Zónák mentése** gombra

### 4. Monitoring indítása

A **📊 Monitoring** fülön:

1. Kattints az **▶️ Indítás** gombra
2. Az élő kép mutatja a detektált LED állapotokat
3. Az állapot kártyák mutatják, hogy melyik zóna aktív

### 5. Home Assistant ellenőrzése

1. Nyisd meg a Home Assistant-ot: **http://[HOME_ASSISTANT_IP]:8123**
2. Menj a **Settings → Devices & Services → MQTT** menüpontra
3. Az eszközök között meg kell jelennie: **ESP32-CAM LED Monitor**
4. A következő entitások láthatók lesznek:
   - `binary_sensor.futes_nappali`
   - `binary_sensor.futes_halo`
   - `binary_sensor.futes_gyerekszoba`
   - `binary_sensor.futes_furdoszoba`

## 📊 Home Assistant Dashboard példa

### Egyszerű Entity Card

```yaml
type: entities
title: 🔴 Fűtés Állapot
entities:
  - entity: binary_sensor.futes_nappali
    name: Nappali
  - entity: binary_sensor.futes_halo
    name: Hálószoba
  - entity: binary_sensor.futes_gyerekszoba
    name: Gyerekszoba
  - entity: binary_sensor.futes_furdoszoba
    name: Fürdőszoba
state_color: true
```

### History Graph - 24 órás előzmények

```yaml
type: history-graph
title: Fűtés előzmények
hours_to_show: 24
entities:
  - entity: binary_sensor.futes_nappali
  - entity: binary_sensor.futes_halo
  - entity: binary_sensor.futes_gyerekszoba
  - entity: binary_sensor.futes_furdoszoba
```

### Statisztika (hány órát volt be a fűtés)

```yaml
sensor:
  - platform: history_stats
    name: Nappali fűtési idő ma
    entity_id: binary_sensor.futes_nappali
    state: "on"
    type: time
    start: "{{ now().replace(hour=0, minute=0, second=0) }}"
    end: "{{ now() }}"
```

Részletesebb Home Assistant konfigurációért lásd: [HOME_ASSISTANT_CONFIG.md](HOME_ASSISTANT_CONFIG.md)

## 🔧 Finomhangolás

### LED Detektálási küszöb módosítása

A webes felületen minden zónához állítható a küszöbérték (threshold):
- **Alacsony érték (10-20)**: Érzékenyebb, sötétebb LED-eket is érzékel
- **Magas érték (40-50)**: Csak erősen világító LED-eket érzékel

### Monitoring gyakoriság

Az `app.py` fájlban módosítható:

```python
def monitoring_thread():
    while monitoring_active:
        process_frame()
        time.sleep(2)  # 2 másodperc → módosítható
```

### ESP32-CAM képminőség

Az ESP32-CAM kódjában:

```cpp
config.frame_size   = FRAMESIZE_VGA;  // VGA (640×480)
config.jpeg_quality = 30;             // 10 (legjobb) - 63 (legrosszabb)
```

## 🐛 Hibaelhárítás

### "Nem sikerült képet letölteni"

- Ellenőrizd, hogy az ESP32-CAM be van-e kapcsolva
- Ellenőrizd az IP címet a webes felületen
- Próbáld meg böngészőből elérni: `http://[ESP32_IP]/`

### "MQTT kapcsolódási hiba"

```bash
# Mosquitto állapot ellenőrzése
sudo systemctl status mosquitto

# Mosquitto újraindítása
sudo systemctl restart mosquitto

# MQTT kapcsolat tesztelése
mosquitto_sub -h localhost -t "homeassistant/#" -v
```

### Home Assistant-ban nem jelennek meg az entitások

1. Ellenőrizd a MQTT integrációt: Settings → Devices & Services → MQTT
2. MQTT reload: Developer Tools → Services → `mqtt.reload`
3. Ellenőrizd a log-okat: Settings → System → Logs

### LED-ek nem detektálódnak helyesen

- Próbáld meg módosítani a küszöbértéket a webes felületen
- Ellenőrizd, hogy a kijelölt terület valóban a LED-et fedi-e
- Nappali fényben lehet, hogy zajosabb a detektálás - sötétebb környezet ajánlott

## 📁 Fájlstruktúra

```
Home_assistant_kiegeszito_feldolgozo/
├── app.py                      # Fő Python alkalmazás
├── requirements.txt            # Python függőségek
├── config.json                 # Konfiguráció (automatikusan generált)
├── templates/
│   └── index.html             # Webes felület
├── HOME_ASSISTANT_CONFIG.md    # Home Assistant részletes konfiguráció
└── README.md                   # Ez a fájl
```

## 🔐 Biztonság

### MQTT Authentication (ajánlott)

```yaml
# Home Assistant configuration.yaml
mqtt:
  broker: localhost
  port: 1883
  username: !secret mqtt_username
  password: !secret mqtt_password
```

Secrets fájlban (`secrets.yaml`):
```yaml
mqtt_username: your_username
mqtt_password: your_password
```

Az alkalmazásban add meg ugyanezeket a hitelesítési adatokat.

## 📈 Teljesítmény

- **Képfeldolgozás**: ~500ms / frame (VGA, 640×480)
- **FPS**: 2 frame/sec ellenőrzési gyakoriság (módosítható)
- **Memória**: ~150MB RAM
- **CPU**: ~5-10% (Raspberry Pi 4)

## 🤝 Támogatás

Ha problémába ütközöl:
1. Ellenőrizd a log-okat a terminálban (`python3 app.py`)
2. Ellenőrizd a Home Assistant log-okat
3. Próbáld meg újraindítani az alkalmazást és a Home Assistant-ot

## 📝 Licenc

MIT License - Szabadon használható és módosítható.

## 🎯 Jövőbeli fejlesztések

- [ ] Telegram bot integráció értesítésekhez
- [ ] Energiafogyasztás számítás fűtési idő alapján
- [ ] Több ESP32-CAM támogatása
- [ ] RESTful API további integrációkhoz
- [ ] Docker konténer
- [ ] Napi/heti/havi statisztikák
- [ ] PWA (Progressive Web App) támogatás

---

**Készítette**: ESP32-CAM LED Monitor Projekt  
**Verzió**: 1.0.0  
**Utolsó frissítés**: 2026. január 24.
