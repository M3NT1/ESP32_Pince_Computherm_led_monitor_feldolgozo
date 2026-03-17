# Changelog

## 1.1.1

- **🔧 Javítva**: `firmware_type` (ESPHome/Custom) választó értékének hiányzó beolvasása és átadása a `run.sh` scriptben, ami miatt az app mindig a `/capture` végpontot kereste. (Bugfix az 1.1.0-hoz)

## 1.1.0

- **🎉 Új**: ESPHome firmware támogatás bevezetése (`firmware_type` konfigurálási lehetőség).
- **🔧 Javítva**: Szimulált ESP32 szerver (`dummy_esp32_server.py`) hozzáadva a lokális tesztelésekhez hardver megkötés nélkül.
- **🔧 Javítva**: Rate-limit finomhangolások - "Kamera Stream Használatban" (HTTP 500) okos lekezelése cache használatával, büntetési (backoff) ciklusok növelése nélkül.

## 1.0.5

- **🔧 Javítva**: Automatikus zóna backup mentés külön fájlba (zones_backup.json)
- **🔧 Javítva**: Zóna helyreállítás backup-ból ha a config.json-ban nincsenek
- **🔧 Javítva**: Monitoring szál duplikáció megakadályozása
- **🔧 Javítva**: MQTT reconnect után monitoring újraindítás ha szükséges
- **📁 Új**: Katasztrófa helyreállítás támogatás zones_backup.json-ból

## 1.0.4

- **🔧 KRITIKUS JAVÍTÁS**: JSON parsing hiba javítása config.json generáláskor
- **✨ Új**: Perzisztens zóna tárolás - zónák megmaradnak újraindítás után
- **✨ Új**: Monitoring állapot perzisztencia - automatikus indítás megmarad
- **🔧 Javítva**: `run.sh` JSON generálás Python script-re cserélve (biztonságos formázás)
- **🔧 Javítva**: `monitoring_active` boolean helyes betöltése (string → boolean konverzió)
- **🔧 Javítva**: Config.json tárolás `/data` könyvtárban (perzisztens volume)
- **🔧 Javítva**: JSON parse hibák részletes hibaüzenettel
- **📝 Változás**: Symlink `/app/config.json` → `/data/config.json` (visszafelé kompatibilitás)

## 1.0.3

- **Új**: Konfigurálható log szint addon beállításokából (DEBUG/INFO/WARNING/ERROR)
- **Javítva**: Logging szintek optimalizálása production környezethez
- **Változás**: Rutin műveletek (ciklus számlálás, várakozás) DEBUG szintre helyezve
- **Változás**: Csak LED változások és hibák jelennek meg INFO/WARNING/ERROR szinten
- **Javítva**: Log spam csökkentése - ~3600 sor/nap helyett csak releváns események

## 1.0.2

- **Új**: "Open Web UI" gomb megjelenítése Home Assistant addon felületen
- **Új**: Ingress támogatás - addon UI közvetlenül Home Assistant-ben
- **Javítva**: Zónák fül mindig tiszta képet használ (nem annotáltat)
- **Új**: MQTT újraregisztráció funkció entitások frissítéséhez
- **Dokumentáció**: Részletes útmutató régi MQTT entitások kézi törléséhez
- **Javítva**: Font változó hibajavítás annotated_snapshot endpoint-ban

## 1.0.1

- **Javítva**: GitHub Actions workflow deprecated flagek javítása
- **Javítva**: config.yaml remote image referencia eltávolítása
- **Javítva**: Docker image pull hiba (denied error)
- **Javítva**: run.sh zones konfiguráció JSON parsing
- **Javítva**: paho-mqtt 1.x és 2.x kompatibilitás
- **Javítva**: MQTT Client backward compatibility

## 1.0.0

- **Új**: Home Assistant Add-on támogatás
- **Új**: HACS Custom Repository integráció
- **Új**: Automatikus konfiguráció Add-on options-ből
- **Új**: Multi-arch Docker támogatás (aarch64, amd64, armhf, armv7)
- **Új**: Webes konfiguráló felület
- **Új**: Többszínű LED detektálás (vörös, zöld, kék, fehér, narancs)
- **Új**: MQTT auto-discovery Home Assistant számára
- **Új**: Valós idejű monitoring 2 perces ciklusokkal
- **Új**: ESP32-CAM stream támogatás
- **Új**: Képfeldolgozás intelligens cache-eléssel
- **Új**: Binary sensor entitások Home Assistanthez
- **Új**: Konfigurálható LED zónák drag-and-drop felülettel
- **Új**: Állítható érzékenység (threshold) zónánként
- **Változás**: config.json automatikus generálása Add-on módban
- **Változás**: Portszám 5000 → 5001
- **Javítva**: ESP32-CAM 2 perces timeout kezelés exponential backoff-fal
- **Javítva**: MQTT újracsatlakozási logika
- **Javítva**: Memória optimalizálás képfeldolgozáshoz

## 0.9.0

- **Kezdeti verzió**: Standalone Python alkalmazás
- OpenCV képfeldolgozás
- Flask webes felület
- MQTT integráció
- Raspberry Pi telepítő script
