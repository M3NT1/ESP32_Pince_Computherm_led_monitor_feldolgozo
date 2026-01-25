# Changelog

Az összes fontos változás ebben a projektben dokumentálva lesz ebben a fájlban.

## [1.0.1] - 2026-01-25

### Javítva
- GitHub Actions workflow deprecated `--all` flag helyettesítése explicit architektúra flagekkel
- `config.yaml` remote image referencia eltávolítása a lokális build engedélyezéséhez
- Docker image pull hiba javítása ("denied" error)
- **run.sh zones konfiguráció JSON parsing hiba javítása**
- Üres zones érték biztonságos kezelése (default: üres tömb)

## [1.0.0] - 2026-01-25

### Hozzáadva
- ✅ Home Assistant Add-on támogatás
- ✅ HACS Custom Repository integráció
- ✅ Automatikus konfiguráció Home Assistant Add-on options-ből
- ✅ Multi-arch Docker image támogatás (aarch64, amd64, armhf, armv7)
- ✅ Webes konfiguráló felület
- ✅ Többszínű LED detektálás (vörös, zöld, kék, fehér, narancs)
- ✅ MQTT auto-discovery Home Assistant számára
- ✅ Valós idejű monitoring
- ✅ ESP32-CAM stream támogatás
- ✅ Képfeldolgozás cache-eléssel
- ✅ Binary sensor entitások Home Assistanthez
- ✅ Konfigurálható LED zónák
- ✅ Állítható érzékenység (threshold)

### Változtatva
- config.json automatikus generálása Add-on módban
- Portszám 5000 → 5001 a kiegészítő alkalmazásokhoz

### Javítva
- ESP32-CAM timeout kezelése
- MQTT újracsatlakozási logika
- Memória optimalizálás képfeldolgozáshoz

## [0.9.0] - 2026-01-20

### Hozzáadva
- Kezdeti verzió standalone Python alkalmazásként
- OpenCV képfeldolgozás
- Flask webes felület
- MQTT integráció
- Raspberry Pi telepítő script

---

A formátum [Keep a Changelog](https://keepachangelog.com/hu/1.0.0/) alapján,
és ez a projekt a [Semantic Versioning](https://semver.org/spec/v2.0.0.html) szabványt követi.
