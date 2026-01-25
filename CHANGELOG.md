# Changelog

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
