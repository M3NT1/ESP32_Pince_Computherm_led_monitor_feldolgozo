# Home Assistant Add-on Telepítési Útmutató

## Gyors Telepítés HACS-el

### 1. HACS telepítése (ha még nincs)

Ha még nincs telepítve a HACS:

1. Látogass el a https://hacs.xyz/docs/setup/download oldalra
2. Kövesd a telepítési útmutatót
3. Indítsd újra a Home Assistantot

### 2. Custom Repository hozzáadása

1. Nyisd meg a Home Assistant webes felületét
2. Kattints a **HACS** menüpontra
3. Kattints a jobb felső sarokban a **⋮** (három pont) ikonra
4. Válaszd a **Custom repositories** menüpontot
5. Add hozzá a következő adatokat:
   - **Repository**: `https://github.com/M3NT1/ESP32_Pince_Computherm_led_monitor_feldolgozo`
   - **Category**: Válaszd ki: `Add-on`
6. Kattints az **Add** gombra

### 3. Add-on telepítése

1. Menj a **Settings** → **Add-ons** menübe
2. Kattints a jobb alsó sarokban az **Add-on Store** gombra
3. Frissítsd az oldalt (ha nem látod azonnal)
4. Keresd meg az **ESP32-CAM LED Monitor** add-ont
5. Kattints rá
6. Kattints az **Install** gombra
7. Várj, amíg a telepítés befejeződik

### 4. Konfiguráció

1. A telepítés után menj a **Configuration** fülre
2. Állítsd be a következő paramétereket:

```yaml
esp32_cam_url: "http://192.168.10.130"  # Az ESP32-CAM IP címe
mqtt_broker: "core-mosquitto"            # Ha beépített Mosquitto-t használsz
mqtt_port: 1883
mqtt_user: ""                            # Opcionális
mqtt_password: ""                        # Opcionális
zones: []                                # Üres marad, a webes felületen állítható be
```

3. Kattints a **Save** gombra

### 5. Add-on indítása

1. Menj az **Info** fülre
2. Kapcsold be a következő opciókat:
   - ✅ **Start on boot** - Automatikus indítás
   - ✅ **Watchdog** - Automatikus újraindítás hiba esetén
3. Kattints a **Start** gombra

### 6. Ellenőrzés

1. Menj a **Log** fülre
2. Ellenőrizd, hogy nincs-e hiba:
   ```
   [OK] MQTT csatlakozva
   Webes felület: http://localhost:5001
   ```

### 7. Webes felület megnyitása

1. Nyisd meg böngészőben: `http://[home-assistant-ip]:5001`
2. Állítsd be a LED zónákat
3. Indítsd el a monitoringot

## Frissítés

### HACS-en keresztül

1. Menj a **HACS** menübe
2. Keresd meg az **ESP32-CAM LED Monitor** add-ont
3. Ha van új verzió, megjelenik egy **Update** gomb
4. Kattints rá és várj a frissítés végéig
5. Menj a **Settings → Add-ons → ESP32-CAM LED Monitor** menübe
6. Kattints a **Restart** gombra

### Manuális frissítés

```bash
cd /addons/esp32cam_led_monitor
git pull
```

Majd a Home Assistantben:
- Settings → Add-ons → ESP32-CAM LED Monitor → Rebuild

## Eltávolítás

1. Menj a **Settings → Add-ons → ESP32-CAM LED Monitor** menübe
2. Állítsd le az add-ont: **Stop**
3. Kattints az **Uninstall** gombra
4. Opcionálisan töröld a HACS Custom Repository-t is

## Hibaelhárítás

### Az add-on nem jelenik meg az Add-on Store-ban

1. Frissítsd az oldalt (Ctrl+F5 / Cmd+Shift+R)
2. Ellenőrizd, hogy megfelelően adtad-e hozzá a Custom Repository-t
3. Várj néhány percet és próbáld újra

### Telepítési hiba

Ha hibát kapsz a telepítés során:

1. Ellenőrizd az internet kapcsolatot
2. Ellenőrizd a lemezterületet: `df -h`
3. Nézd meg a Supervisor logokat: Settings → System → Logs

### Build hiba

Ha Docker build hiba történik:

```bash
# SSH-n keresztül csatlakozz a Home Assistant host-hoz
docker system prune -a
```

Majd próbáld újra.

## Kapcsolódó Dokumentáció

- [README.md](README.md) - Általános leírás
- [DOCS.md](DOCS.md) - Részletes konfiguráció
- [HOME_ASSISTANT_CONFIG.md](HOME_ASSISTANT_CONFIG.md) - Home Assistant példák
