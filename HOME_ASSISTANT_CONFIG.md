# Home Assistant Konfiguráció
# ESP32-CAM LED Monitor MQTT Integráció

## Automatikus Device Discovery
Az alkalmazás automatikusan regisztrálja az eszközöket a Home Assistant-ban MQTT auto-discovery használatával.

## Manuális konfiguráció (opcionális)

### 1. MQTT Broker beállítása
Győződj meg róla, hogy az MQTT broker (pl. Mosquitto) fut a Home Assistant-on:

```yaml
# configuration.yaml
mqtt:
  broker: localhost
  port: 1883
  discovery: true
  discovery_prefix: homeassistant
```

### 2. Binary Sensor-ok (automatikusan létrejönnek)
Az alábbi érzékelők automatikusan megjelennek, amikor a monitoring elindul:

```yaml
# Példa - ezek automatikusan létrejönnek
binary_sensor:
  - platform: mqtt
    name: "Fűtés Nappali"
    state_topic: "homeassistant/binary_sensor/led_monitor/zone_xxxxx/state"
    device_class: heat
    payload_on: "ON"
    payload_off: "OFF"
    icon: mdi:radiator
```

### 3. History és Recorder beállítása
A fűtés történet nyomon követéséhez:

```yaml
# configuration.yaml
recorder:
  db_url: sqlite:////config/home-assistant_v2.db
  purge_keep_days: 90
  include:
    entity_globs:
      - binary_sensor.futes_*

history:
  include:
    entity_globs:
      - binary_sensor.futes_*
```

### 4. Lovelace Dashboard példa

```yaml
type: vertical-stack
cards:
  - type: entities
    title: 🔴 Fűtés Monitoring
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

  - type: history-graph
    title: Fűtés előzmények (24 óra)
    hours_to_show: 24
    entities:
      - entity: binary_sensor.futes_nappali
      - entity: binary_sensor.futes_halo
      - entity: binary_sensor.futes_gyerekszoba
      - entity: binary_sensor.futes_furdoszoba

  - type: custom:mini-graph-card
    name: Fűtési idő ma
    hours_to_show: 24
    points_per_hour: 4
    entities:
      - entity: binary_sensor.futes_nappali
        name: Nappali
      - entity: binary_sensor.futes_halo
        name: Hálószoba
```

### 5. Automatizációk

#### Értesítés, ha fűtés bekapcsol
```yaml
automation:
  - alias: "Értesítés fűtés bekapcsolás"
    trigger:
      - platform: state
        entity_id:
          - binary_sensor.futes_nappali
          - binary_sensor.futes_halo
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "🔴 Fűtés bekapcsolva"
          message: "{{ trigger.to_state.attributes.friendly_name }} fűtés elindult"
```

#### Napi statisztika
```yaml
automation:
  - alias: "Napi fűtési összefoglaló"
    trigger:
      - platform: time
        at: "23:55:00"
    action:
      - service: notify.mobile_app
        data:
          title: "📊 Mai fűtési statisztika"
          message: >
            Nappali: {{ states.binary_sensor.futes_nappali.last_changed }}
            Háló: {{ states.binary_sensor.futes_halo.last_changed }}
```

### 6. Template Sensor-ok (opcionális)

#### Fűtési idő számítása
```yaml
sensor:
  - platform: history_stats
    name: Nappali fűtési idő ma
    entity_id: binary_sensor.futes_nappali
    state: "on"
    type: time
    start: "{{ now().replace(hour=0, minute=0, second=0) }}"
    end: "{{ now() }}"

  - platform: history_stats
    name: Háló fűtési idő ma
    entity_id: binary_sensor.futes_halo
    state: "on"
    type: time
    start: "{{ now().replace(hour=0, minute=0, second=0) }}"
    end: "{{ now() }}"
```

### 7. MQTT Explorer (debug célokra)
Topic struktúra:
```
homeassistant/
  binary_sensor/
    led_monitor/
      zone_1234567890/
        config      (auto-discovery konfiguráció)
        state       (ON/OFF)
      zone_9876543210/
        config
        state
```

### 8. Újraindítás után
```bash
# Home Assistant újraindítása
ha core restart

# MQTT integráció újratöltése
Developer Tools -> Services -> mqtt.reload
```

## Hibaelhárítás

### MQTT kapcsolat ellenőrzése
```bash
# Mosquitto kliens telepítése
apt-get install mosquitto-clients

# Topic figyelése
mosquitto_sub -h localhost -t "homeassistant/binary_sensor/led_monitor/#" -v

# Teszt üzenet küldése
mosquitto_pub -h localhost -t "homeassistant/binary_sensor/led_monitor/test/state" -m "ON"
```

### Log-ok ellenőrzése
```yaml
# configuration.yaml
logger:
  default: info
  logs:
    homeassistant.components.mqtt: debug
```

## Kiegészítő integrációk

### Node-RED integráció
A Node-RED-ben létrehozhatsz további automatizációkat az MQTT topic-ok figyelésével.

### InfluxDB + Grafana
Hosszú távú adattároláshoz és részletes analitikához:
```yaml
influxdb:
  host: localhost
  port: 8086
  database: homeassistant
  include:
    entity_globs:
      - binary_sensor.futes_*
```

## Frissítés és karbantartás
- A zónák újrakonfigurálása után a Discovery automatikusan frissül
- Az MQTT retained flag-ek biztosítják, hogy a Home Assistant újraindítás után is megkapja az utolsó állapotot
