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

bashio::log.info "ESP32-CAM URL: ${ESP32_CAM_URL}"
bashio::log.info "MQTT Broker: ${MQTT_BROKER}:${MQTT_PORT}"

# Zones konfiguráció biztonságos beolvasása
ZONES=$(bashio::config 'zones' '[]')
if [ -z "$ZONES" ] || [ "$ZONES" = "null" ]; then
  ZONES="[]"
fi

# Config.json létrehozása
cat > /app/config.json <<EOF
{
  "esp32_cam_url": "${ESP32_CAM_URL}",
  "mqtt_broker": "${MQTT_BROKER}",
  "mqtt_port": ${MQTT_PORT},
  "mqtt_user": "${MQTT_USER}",
  "mqtt_password": "${MQTT_PASSWORD}",
  "zones": ${ZONES}
}
EOF

bashio::log.info "Konfiguráció betöltve"

# Python alkalmazás indítása
cd /app
exec python3 app.py
