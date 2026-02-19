#!/usr/bin/with-contenv bashio
# ==============================================================================
# ESP32-CAM LED Monitor - Home Assistant Add-on indító script
# ==============================================================================

bashio::log.info "ESP32-CAM LED Monitor indítása..."

# Konfiguráció betöltése a Home Assistant options-ből
CONFIG_PATH="/data/options.json"

# Config.json generálása az add-on beállításokból
ESP32_CAM_URL=$(bashio::config 'esp32_cam_url')
MQTT_BROKER=$(bashio::config 'mqtt_broker')
MQTT_PORT=$(bashio::config 'mqtt_port')
MQTT_USER=$(bashio::config 'mqtt_user')
MQTT_PASSWORD=$(bashio::config 'mqtt_password')
LOG_LEVEL=$(bashio::config 'log_level' 'INFO')

bashio::log.info "ESP32-CAM URL: ${ESP32_CAM_URL}"
bashio::log.info "MQTT Broker: ${MQTT_BROKER}:${MQTT_PORT}"
bashio::log.info "Log Level: ${LOG_LEVEL}"

# Zones konfiguráció biztonságos beolvasása
ZONES=$(bashio::config 'zones' '[]')
if [ -z "$ZONES" ] || [ "$ZONES" = "null" ]; then
  ZONES="[]"
fi

# INTELLIGENS CONFIG MERGE: meglévő zónák megtartása
# PERZISZTENS TÁRHELY: /data könyvtár (Home Assistant Add-on perzisztens volume)
EXISTING_CONFIG="/data/config.json"
EXISTING_ZONES="[]"
EXISTING_MONITORING="false"

if [ -f "$EXISTING_CONFIG" ]; then
  bashio::log.info "Meglévő config.json észlelve - zónák és monitoring állapot megőrzése..."
  
  # Meglévő zónák kinyerése (ha vannak)
  EXISTING_ZONES=$(python3 -c "
import json
try:
    with open('$EXISTING_CONFIG', 'r') as f:
        config = json.load(f)
        zones = config.get('zones', [])
        # Ha vannak meglévő zónák, azokat használjuk
        if zones and len(zones) > 0:
            print(json.dumps(zones))
        else:
            print('[]')
except:
    print('[]')
" 2>/dev/null || echo "[]")
  
  # Meglévő monitoring állapot kinyerése
  EXISTING_MONITORING=$(python3 -c "
import json
try:
    with open('$EXISTING_CONFIG', 'r') as f:
        config = json.load(f)
        print('true' if config.get('monitoring_active', False) else 'false')
except:
    print('false')
" 2>/dev/null || echo "false")
  
  # Ha vannak meglévő zónák, azokat használjuk (addon config zones NEM írja felül!)
  if [ "$EXISTING_ZONES" != "[]" ]; then
    bashio::log.info "Meglévő zónák megtalálva és megőrizve ($(echo $EXISTING_ZONES | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "?") db)"
    ZONES="$EXISTING_ZONES"
  else
    bashio::log.info "Nincs meglévő zóna - addon config zones használata"
  fi
  
  bashio::log.info "Monitoring állapot megőrizve: $EXISTING_MONITORING"
else
  bashio::log.info "Új config.json létrehozása"
  EXISTING_MONITORING="false"
fi

# ===== ZÓNA BACKUP HELYREÁLLÍTÁS =====
# Ha EXISTING_ZONES üres, próbáljuk a backup fájlból
ZONES_BACKUP="/data/zones_backup.json"
if [ "$EXISTING_ZONES" = "[]" ] && [ -f "$ZONES_BACKUP" ]; then
  bashio::log.info "Zóna backup fájl észlelve - helyreállítás..."
  EXISTING_ZONES=$(python3 -c "
import json
try:
    with open('$ZONES_BACKUP', 'r') as f:
        backup = json.load(f)
        zones = backup.get('zones', [])
        if zones:
            print(json.dumps(zones))
        else:
            print('[]')
except:
    print('[]')
" 2>/dev/null || echo "[]")

  EXISTING_MONITORING=$(python3 -c "
import json
try:
    with open('$ZONES_BACKUP', 'r') as f:
        backup = json.load(f)
        print('true' if backup.get('monitoring_active', False) else 'false')
except:
    print('false')
" 2>/dev/null || echo "false")

  if [ "$EXISTING_ZONES" != "[]" ]; then
    bashio::log.info "Zónák helyreállítva backup-ból ($(echo $EXISTING_ZONES | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "?") db)"
    ZONES="$EXISTING_ZONES"
  fi
fi

# Config.json létrehozása MERGE-elt adatokkal - BIZTONSÁGOS PYTHON MÓDSZER
python3 - <<PYTHON_SCRIPT
import json
import sys

try:
    # Zones parse-olása
    zones_str = '''${ZONES}'''
    try:
        zones = json.loads(zones_str) if zones_str.strip() else []
    except:
        zones = []
    
    # Monitoring boolean parse-olása
    monitoring_active = '''${EXISTING_MONITORING}'''.lower() == 'true'
    
    # Config objektum összeállítása
    config = {
        "esp32_cam_url": "${ESP32_CAM_URL}",
        "mqtt_broker": "${MQTT_BROKER}",
        "mqtt_port": int(${MQTT_PORT}),
        "mqtt_user": "${MQTT_USER}",
        "mqtt_password": "${MQTT_PASSWORD}",
        "log_level": "${LOG_LEVEL}",
        "zones": zones,
        "monitoring_active": monitoring_active
    }
    
    # JSON fájl írása
    with open('/data/config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Config.json sikeresen létrehozva ({len(zones)} zóna, monitoring: {monitoring_active})")
    sys.exit(0)
except Exception as e:
    print(f"✗ Hiba a config.json létrehozásakor: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT

if [ $? -eq 0 ]; then
    bashio::log.info "Konfiguráció betöltve és merge-elve"
    # Symlink létrehozása /app/config.json -> /data/config.json (visszafelé kompatibilitás)
    ln -sf /data/config.json /app/config.json
else
    bashio::log.error "Hiba a konfiguráció létrehozásakor"
    exit 1
fi

# Python alkalmazás indítása
cd /app
exec python3 app.py
