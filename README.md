# ESP32-CAM LED Monitor - Home Assistant Add-on

![Version](https://img.shields.io/badge/version-1.0.5-blue.svg)
![Supports aarch64 Architecture](https://img.shields.io/badge/aarch64-yes-green.svg)
![Supports amd64 Architecture](https://img.shields.io/badge/amd64-yes-green.svg)
![Supports armhf Architecture](https://img.shields.io/badge/armhf-yes-green.svg)
![Supports armv7 Architecture](https://img.shields.io/badge/armv7-yes-green.svg)

ESP32-CAM alapú LED állapot monitor Computherm fűtésszabályozóhoz, Home Assistant integrációval.

## 🆕 Legújabb frissítés: v1.0.5 (2026.02.19)

**🔧 JAVÍTÁSOK:**
- ✅ **Automatikus zóna backup** - Külön backup fájl a zónák védelmére
- ✅ **Katasztrófa helyreállítás** - Zónák visszaállítása backup-ból szükség esetén
- ✅ **Monitoring szál védelem** - Duplikált szálak megakadályozása
- ✅ **MQTT reconnect fix** - Monitoring újraindul kapcsolat visszaállításkor

**ℹ️ FONTOS:** Ez a verzió extra védelmet ad a zóna konfigurációk számára!

## 📋 Funkciók

- 🎥 Valós idejű ESP32-CAM képfeldolgozás
- 🔴 Többszínű LED detektálás (vörös, zöld, kék, fehér, narancs)
- 📊 Webes felület a zónák konfigurálásához
- 💾 **Perzisztens zóna tárolás** - zónák megmaradnak újraindítás után
- 🔄 **Automatikus monitoring indítás** - az állapot megmarad újraindítás után
- 🏠 Automatikus Home Assistant integráció MQTT-n keresztül
- ⚡ Valós idejű állapot frissítés (2 percenként)
- 📦 Egyszerű telepítés HACS-en keresztül
- 🔧 Konfigurálható log szintek (DEBUG/INFO/WARNING/ERROR)

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

### 1. HACS telepítés (ajánlott)

1. Nyisd meg a HACS-t a Home Assistantben
2. Kattints a jobb felső sarokban a három pontra (⋮)
3. Válaszd a **"Custom repositories"** menüpontot
4. Add hozzá a következő repository-t:
   - **URL**: `https://github.com/M3NT1/ESP32_Pince_Computherm_led_monitor_feldolgozo`
   - **Category**: `Add-on`
5. Kattints az **"Add"** gombra
6. Keresd meg az **"ESP32-CAM LED Monitor"** add-ont
7. Kattints a **"Download"** gombra
8. Menj a **Settings → Add-ons** menübe
9. Keress rá az **"ESP32-CAM LED Monitor"** add-onra
10. Kattints rá és állítsd be a konfigurációt (lásd alább)
11. Indítsd el az add-ont

### 2. Manuális telepítés

```bash
cd /addons
git clone https://github.com/M3NT1/ESP32_Pince_Computherm_led_monitor_feldolgozo.git esp32cam_led_monitor
```

Majd a Home Assistant Supervisor-ban:
- **Settings → Add-ons → Add-on Store** (jobb alsó sarok)
- **Refresh**
- Keresd meg az **"ESP32-CAM LED Monitor"** add-ont

## ⚙️ Konfiguráció

### Alapbeállítások

Az add-on konfigurációs felületén (Settings → Add-ons → ESP32-CAM LED Monitor → Configuration):

```yaml
esp32_cam_url: "http://192.168.10.130"
mqtt_broker: "core-mosquitto"
mqtt_port: 1883
mqtt_user: ""
mqtt_password: ""
zones: []
```

### LED zónák beállítása

1. Indítsd el az add-ont
2. Nyisd meg a webes felületet: `http://[home-assistant-ip]:5001`
3. Kattints a **"Zónák szerkesztése"** gombra
4. Állítsd be a LED zónákat az egérrel húzva
5. Mentsd el a konfigurációt
6. ✅ **A zónák automatikusan perzisztensek** - megmaradnak újraindítás után!

### Monitoring indítása

1. A webes felületen kattints a **"Monitoring indítása"** gombra
2. ✅ **Az állapot automatikusan perzisztens** - újraindítás után is bekapcsolva marad!

### MQTT konfiguráció

**Ha a beépített Mosquitto brokert használod:**
- MQTT broker: `core-mosquitto`
- MQTT user/password: üres (ha nincs beállítva)

**Ha külső MQTT brokert használsz:**
- Állítsd be az IP címet vagy hostname-t
- Add meg a felhasználónevet és jelszót

## 🏠 Home Assistant integráció

Az add-on automatikusan létrehozza a binary sensor entitásokat:

```yaml
binary_sensor.futes_pince
binary_sensor.futes_nappali
binary_sensor.futes_haloszoba
# stb...
```

### Lovelace card példa

```yaml
type: entities
title: Fűtés állapot
entities:
  - entity: binary_sensor.futes_pince
  - entity: binary_sensor.futes_nappali
  - entity: binary_sensor.futes_haloszoba
```

### Automatizáció példa

```yaml
automation:
  - alias: "Értesítés fűtés bekapcsoláskor"
    trigger:
      - platform: state
        entity_id: binary_sensor.futes_pince
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          message: "A pince fűtés bekapcsolt"
```

## 📱 ESP32-CAM konfiguráció

Az ESP32-CAM-et úgy kell beállítani, hogy HTTP stream-et szolgáltasson a `/` endpointon.

Példa Arduino kód: (ha szükséges, kérd el külön)

## 🔧 Hibaelhárítás

### Zónák elvesznek újraindítás után (≤ v1.0.3)

✅ **Megoldva v1.0.4-ben!** Frissítsd az add-ont a legújabb verzióra:
1. **Settings → Add-ons → ESP32-CAM LED Monitor**
2. Kattints a **"Check for updates"** gombra
3. Ha elérhető az új verzió, kattints a **"Update"** gombra
4. Indítsd újra az add-ont

### Az add-on nem indul el

1. Ellenőrizd a logokat: **Settings → Add-ons → ESP32-CAM LED Monitor → Log**
2. Ellenőrizd az MQTT kapcsolatot
3. Ellenőrizd az ESP32-CAM elérhetőségét
4. Ha "JSON parsing error" látható a logokban, frissítsd v1.0.4-re

### Az ESP32-CAM nem elérhető

1. Pingeld az IP címet: `ping 192.168.10.130`
2. Nyisd meg böngészőben: `http://192.168.10.130`
3. Ellenőrizd a tápellátást
4. Ellenőrizd a WiFi kapcsolatot

### MQTT entitások nem jelennek meg

1. Ellenőrizd, hogy a Mosquitto broker fut-e
2. Restart Home Assistant
3. Ellenőrizd az MQTT integráció beállításait: **Settings → Devices & Services → MQTT**

### LED detektálás nem működik megfelelően

1. Nyisd meg a webes felületet: `http://[home-assistant-ip]:5001`
2. Nézd meg az előnézeti képet (zónák kirajzolva)
3. Állítsd be a zónák méretét és pozícióját
4. Próbáld ki a különböző LED típusokat (auto, red, green, blue, white, orange)
5. Módosítsd a küszöbértéket (threshold) 10-100 között

## 💾 Rendszerkövetelmények

- Home Assistant OS / Supervised
- MQTT broker (pl. Mosquitto)
- ESP32-CAM HTTP stream képességgel
- Min. 512 MB RAM (Raspberry Pi 3+, 4 ajánlott)

## 🖥️ Támogatott architektúrák

- ✅ aarch64 (Raspberry Pi 3/4 64-bit)
- ✅ amd64 (x86-64)
- ✅ armhf (Raspberry Pi 32-bit)
- ✅ armv7 (Raspberry Pi 2/3 32-bit)

## 📞 Támogatás

- 🐛 **GitHub Issues**: https://github.com/M3NT1/ESP32_Pince_Computherm_led_monitor_feldolgozo/issues
- 📖 **Dokumentáció**: [DOCS.md](DOCS.md)
- 🔧 **Home Assistant**: https://www.home-assistant.io

## � Verzió történet
### v1.0.5 (2026.02.19) - Zóna védelem
- 🔧 Automatikus zóna backup (zones_backup.json)
- 🔧 Katasztrófa helyreállítás
- 🔧 Monitoring szál duplikáció fix
- 🔧 MQTT reconnect monitoring fix
### v1.0.4 (2026.02.13) - KRITIKUS JAVÍTÁS
- 🔧 **Perzisztens zóna tárolás** - zónák megmaradnak újraindítás után
- 🔧 **Monitoring állapot perzisztencia** - automatikus indítás megmarad
- 🔧 JSON parsing hiba javítása
- 🔧 Config.json tárolás `/data` könyvtárban

### v1.0.3 (2026.01.25)
- ⚙️ Konfigurálható log szintek
- 🔧 Logging optimalizálás production környezethez

### v1.0.2 (2026.01.20)
- 🌐 Ingress támogatás
- 🔧 MQTT újraregisztráció funkció
- 🎨 UI javítások

### v1.0.1 (2026.01.15)
- 🔧 MQTT kompatibilitási javítások
- 🔧 Config parsing javítások

### v1.0.0 (2026.01.10)
- 🎉 Első stabil kiadás

## �📄 Licenc

MIT License

## 🙏 Köszönetnyilvánítás

- Home Assistant közösség
- OpenCV projekt
- Flask framework
- Paho MQTT

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

---

## 📚 További dokumentáció

- 📖 [DOCS.md](DOCS.md) - Add-on részletes dokumentáció
- 🏠 [HOME_ASSISTANT_CONFIG.md](HOME_ASSISTANT_CONFIG.md) - Home Assistant példák
- 🚀 [RASPBERRY_PI_INSTALL.md](RASPBERRY_PI_INSTALL.md) - Manuális telepítés (ha nem add-ont használsz)
- 📝 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Gyors áttekintés

---

**Készítette:** M3NT1  
**Repository:** https://github.com/M3NT1/ESP32_Pince_Computherm_led_monitor_feldolgozo  
**Licenc:** MIT

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
