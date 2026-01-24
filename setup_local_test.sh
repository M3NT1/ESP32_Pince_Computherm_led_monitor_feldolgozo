#!/bin/bash
#
# ESP32-CAM LED Monitor - Helyi Tesztelési Környezet (Mac/Linux)
# Kipróbálható Home Assistant nélkül is!
#

set -e

echo "=============================================="
echo "ESP32-CAM LED Monitor - Helyi Teszt Telepítő"
echo "=============================================="
echo ""

# Szín kódok
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}[1/4] Python verzió ellenőrzése...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "Python3 nincs telepítve!"
    echo "Telepítsd: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "Talált: $PYTHON_VERSION"

echo -e "${GREEN}[2/4] Virtuális környezet létrehozása...${NC}"
if [ -d "venv" ]; then
    echo "Már létezik venv, törlöm és újra létrehozom..."
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

echo -e "${GREEN}[3/4] Python függőségek telepítése...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}[4/4] Teszt konfiguráció létrehozása...${NC}"
if [ ! -f "config.json" ]; then
    cat > config.json <<EOL
{
  "zones": [],
  "esp32_cam_url": "http://192.168.10.130",
  "mqtt_broker": "localhost",
  "mqtt_port": 1883,
  "mqtt_user": "",
  "mqtt_password": ""
}
EOL
    echo "config.json létrehozva"
fi

echo ""
echo -e "${GREEN}=============================================="
echo "✅ Telepítés kész!"
echo "==============================================${NC}"
echo ""
echo "Következő lépések:"
echo ""
echo "1. Aktiváld a virtuális környezetet:"
echo "   source venv/bin/activate"
echo ""
echo "2. Indítsd el az alkalmazást:"
echo "   python3 app.py"
echo ""
echo "3. Nyisd meg böngészőben:"
echo "   http://localhost:5000"
echo ""
echo -e "${YELLOW}FONTOS:${NC} MQTT nélkül is működik, csak a Home Assistant"
echo "integráció nem lesz aktív. A webes felület teljesen használható!"
echo ""
echo "ESP32-CAM IP cím beállítása:"
echo "   A webes felületen: ⚙️ Beállítás fül"
echo ""
