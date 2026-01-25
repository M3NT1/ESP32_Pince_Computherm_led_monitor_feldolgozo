# 📦 GitHub Repository Beállítások

## Repository Settings

### About (Névjegy)

**Description:**
```
ESP32-CAM alapú LED monitor Computherm fűtésszabályozóhoz - Home Assistant Add-on MQTT integrációval
```

**Website:**
```
https://github.com/M3NT1/ESP32_Pince_Computherm_led_monitor_feldolgozo
```

**Topics (címkék):**
```
home-assistant
home-automation
esp32-cam
mqtt
opencv
python
flask
raspberry-pi
smart-home
led-monitor
computherm
heating-control
hacs
addon
computer-vision
```

### Features (Funkciók)

- ✅ **Releases** - Engedélyezve (verziókezelés)
- ✅ **Packages** - Engedélyezve (Docker image-ek)
- ✅ **Deployments** - Opcionális
- ❌ **Discussions** - Opcionálisan engedélyezhető
- ❌ **Projects** - Nem szükséges
- ❌ **Wiki** - Nem szükséges (dokumentáció a repo-ban)

### Social Preview

Tölts fel egy banner képet (1280×640 px):
- ESP32-CAM kép
- Home Assistant logó
- Projekt neve

## Első Release Létrehozása

### 1. GitHub-on

1. Menj a repository **Releases** oldalára
2. Kattints a **"Draft a new release"** gombra
3. Állítsd be:
   - **Tag**: `v1.0.0`
   - **Title**: `v1.0.0 - Első Home Assistant Add-on Release`
   - **Description**: Másold be a CHANGELOG.md [1.0.0] verzióját
4. Jelöld be: **Set as the latest release**
5. Kattints a **"Publish release"** gombra

### 2. Docker Image Build

A GitHub Actions automatikusan elkészíti a Docker image-eket minden architektúrához:
- `ghcr.io/m3nt1/esp32cam-led-monitor-aarch64:1.0.0`
- `ghcr.io/m3nt1/esp32cam-led-monitor-amd64:1.0.0`
- `ghcr.io/m3nt1/esp32cam-led-monitor-armhf:1.0.0`
- `ghcr.io/m3nt1/esp32cam-led-monitor-armv7:1.0.0`

## GitHub Settings

### Packages (Container Registry)

1. Menj a **Settings** → **Packages** menübe
2. Ellenőrizd, hogy a **Container registry** engedélyezve van-e
3. A publikált image-ek láthatók lesznek a **Packages** szekcióban

### GitHub Pages (opcionális)

Ha szeretnél dokumentációs weboldalt:

1. **Settings** → **Pages**
2. **Source**: Deploy from a branch
3. **Branch**: `main` / `docs` (ha van)
4. **Folder**: `/` vagy `/docs`

## README Badge-ek

A következő badge-eket használhatod a README.md fájlban:

```markdown
![GitHub release](https://img.shields.io/github/v/release/M3NT1/ESP32_Pince_Computherm_led_monitor_feldolgozo)
![GitHub stars](https://img.shields.io/github/stars/M3NT1/ESP32_Pince_Computherm_led_monitor_feldolgozo)
![GitHub issues](https://img.shields.io/github/issues/M3NT1/ESP32_Pince_Computherm_led_monitor_feldolgozo)
![GitHub license](https://img.shields.io/github/license/M3NT1/ESP32_Pince_Computherm_led_monitor_feldolgozo)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Add--on-blue)
![HACS](https://img.shields.io/badge/HACS-Custom-orange)
```

## Következő Lépések

1. ✅ Push-old a kódot a GitHub repo-ba
2. ✅ Hozz létre egy `v1.0.0` release-t
3. ✅ Várj míg a GitHub Actions befejezi a build-et
4. ✅ Teszteld a telepítést HACS-en keresztül
5. ✅ Frissítsd a dokumentációt ha szükséges

## Kapcsolódó Linkek

- 🏠 Home Assistant Add-on dokumentáció: https://developers.home-assistant.io/docs/add-ons
- 📦 HACS dokumentáció: https://hacs.xyz/docs/publish/addon
- 🐳 Docker dokumentáció: https://docs.docker.com/
- 🔧 GitHub Actions: https://docs.github.com/en/actions
