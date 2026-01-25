# ESP32-CAM LED Monitor - Home Assistant Add-on

## Konfiguráció

### ESP32-CAM beállítások

**esp32_cam_url**: Az ESP32-CAM teljes URL címe (pl. `http://192.168.10.130`)

### MQTT beállítások

**mqtt_broker**: MQTT broker címe
- Home Assistant beépített MQTT használata esetén: `core-mosquitto`
- Külső MQTT broker esetén: IP cím vagy hostname

**mqtt_port**: MQTT port (alapértelmezett: 1883)

**mqtt_user**: MQTT felhasználónév (opcionális)

**mqtt_password**: MQTT jelszó (opcionális)

### LED zónák beállítása

A zónák a webes felületen konfigurálhatók: `http://[home-assistant-ip]:5001`

Példa konfiguráció:

```yaml
esp32_cam_url: "http://192.168.10.130"
mqtt_broker: "core-mosquitto"
mqtt_port: 1883
mqtt_user: ""
mqtt_password: ""
zones:
  - name: "Pince"
    id: "led_pince"
    x: 100
    y: 150
    width: 50
    height: 50
    threshold: 30
    led_type: "auto"
  - name: "Nappali"
    id: "led_nappali"
    x: 200
    y: 150
    width: 50
    height: 50
    threshold: 30
    led_type: "red"
```

## Használat

1. Telepítsd az add-ont
2. Konfiguráld az ESP32-CAM IP címét
3. Konfiguráld az MQTT kapcsolatot
4. Indítsd el az add-ont
5. Nyisd meg a webes felületet: `http://[home-assistant-ip]:5001`
6. Állítsd be a LED zónákat a webes felületen
7. Indítsd el a monitoringot

## Home Assistant integráció

Az add-on automatikusan létrehozza a binary sensor entitásokat Home Assistantben:
- `binary_sensor.futes_[zona_név]`

Ezek az entitások használhatók automatizációkban, card-okban stb.

## Hibaelhárítás

### Az add-on nem indul el

Ellenőrizd a logokat: **Settings → Add-ons → ESP32-CAM LED Monitor → Log**

### Az ESP32-CAM nem elérhető

- Ellenőrizd, hogy az ESP32-CAM be van-e kapcsolva
- Ellenőrizd az IP címet
- Próbáld meg böngészőből megnyitni: `http://[esp32-cam-ip]`

### MQTT kapcsolódási hiba

- Ellenőrizd, hogy a Mosquitto broker fut-e
- Ellenőrizd az MQTT beállításokat
- Ha külső MQTT brokert használsz, ellenőrizd a tűzfal beállításokat

## Támogatás

GitHub: https://github.com/M3NT1/ESP32_Pince_Computherm_led_monitor_feldolgozo
