#!/bin/bash
#
# ⚠️  FIGYELEM: EZ A TELEPÍTŐ SCRIPT ELAVULT!
#
# Az ESP32-CAM LED Monitor mostantól Home Assistant Add-on formátumban érhető el.
# 
# 🎉 AJÁNLOTT TELEPÍTÉSI MÓDSZER: HACS
#
# Kérjük, használd a HACS-t (Home Assistant Community Store) a telepítéshez:
#
# 1. Nyisd meg a HACS-t Home Assistantben
# 2. Menj a Custom repositories menübe (⋮ → Custom repositories)
# 3. Add hozzá ezt a repository-t:
#    URL: https://github.com/M3NT1/ESP32_Pince_Computherm_led_monitor_feldolgozo
#    Category: Add-on
# 4. Telepítsd az add-ont a HACS-ből
# 5. Konfiguráld és indítsd el
#
# 📖 Részletes útmutató:
# - README.md
# - HACS_INSTALL.md
# - QUICKSTART.md
#
# 🆘 Segítségre van szükséged?
# GitHub Issues: https://github.com/M3NT1/ESP32_Pince_Computherm_led_monitor_feldolgozo/issues
#
# ============================================================================

echo "=============================================="
echo "⚠️  FIGYELEM: ELAVULT TELEPÍTŐ"
echo "=============================================="
echo ""
echo "Ez a telepítő script ELAVULT és NEM AJÁNLOTT többé."
echo ""
echo "Az ESP32-CAM LED Monitor mostantól Home Assistant"
echo "Add-on formátumban érhető el HACS-en keresztül."
echo ""
echo "=============================================="
echo "✅ AJÁNLOTT TELEPÍTÉSI MÓDSZER"
echo "=============================================="
echo ""
echo "1. Telepítsd a HACS-t (ha még nincs):"
echo "   https://hacs.xyz/docs/setup/download"
echo ""
echo "2. Add hozzá a Custom Repository-t:"
echo "   HACS → ⋮ → Custom repositories"
echo "   URL: https://github.com/M3NT1/ESP32_Pince_Computherm_led_monitor_feldolgozo"
echo "   Category: Add-on"
echo ""
echo "3. Telepítsd az Add-ont:"
echo "   Settings → Add-ons → Add-on Store"
echo "   Keresés: 'ESP32-CAM LED Monitor'"
echo ""
echo "4. Konfiguráld és indítsd el"
echo ""
echo "=============================================="
echo "📖 Részletes dokumentáció:"
echo "=============================================="
echo ""
echo "  • README.md         - Általános leírás"
echo "  • HACS_INSTALL.md   - HACS telepítési útmutató"
echo "  • QUICKSTART.md     - 5 perces gyors útmutató"
echo "  • DOCS.md           - Részletes konfiguráció"
echo ""
echo "=============================================="
echo ""
read -p "Biztos folytatni szeretnéd az elavult telepítést? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo ""
    echo "Telepítés megszakítva. Használd a HACS-t!"
    echo ""
    exit 1
fi

echo ""
echo "⚠️  OK, folytatjuk az elavult telepítést..."
echo "⚠️  Kérjük, fontold meg a HACS használatát a jövőben!"
echo ""
sleep 3

# Az eredeti telepítő script folytatódik innen...
# (A régi kód megtartva kompatibilitás miatt)

set -e

echo "=============================================="
echo "ESP32-CAM LED Monitor - Raspberry Pi Telepítő"
echo "=============================================="
echo ""

# Szín kódok
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Ellenőrzések
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Ezt a scriptet root jogosultsággal kell futtatni!${NC}"
    echo "Használd: sudo ./install_rpi.sh"
    exit 1
fi

# Munkakönyvtár
INSTALL_DIR="/opt/esp32cam_led_monitor"
SERVICE_NAME="esp32cam-led-monitor"
USER="homeassistant"

# Ha nincs homeassistant user, használjuk a pi usert
if ! id "$USER" &>/dev/null; then
    USER="pi"
    echo -e "${YELLOW}Homeassistant user nem található, használom: $USER${NC}"
fi

echo -e "${GREEN}[1/6] Rendszer frissítése...${NC}"
apt-get update
apt-get upgrade -y

echo -e "${GREEN}[2/6] Szükséges csomagok telepítése...${NC}"
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    libatlas-base-dev \
    libjpeg-dev \
    zlib1g-dev \
    libopenjp2-7 \
    libtiff5 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libcanberra-gtk-module \
    libcanberra-gtk3-module

echo -e "${GREEN}[3/6] Alkalmazás könyvtár létrehozása: $INSTALL_DIR${NC}"
mkdir -p $INSTALL_DIR
cp -r ./* $INSTALL_DIR/
cd $INSTALL_DIR

echo -e "${GREEN}[4/6] Python virtuális környezet létrehozása...${NC}"
python3 -m venv venv
source venv/bin/activate

echo -e "${GREEN}[5/6] Python függőségek telepítése (ez eltarthat néhány percig)...${NC}"
pip install --upgrade pip
pip install wheel
# OpenCV Raspberry Pi-re optimalizálva
pip install opencv-python-headless==4.8.1.78
pip install Flask==3.0.0
pip install numpy==1.24.3
pip install requests==2.31.0
pip install paho-mqtt==1.6.1

# Jogosultságok beállítása
chown -R $USER:$USER $INSTALL_DIR

echo -e "${GREEN}[6/6] Systemd service létrehozása...${NC}"
cat > /etc/systemd/system/${SERVICE_NAME}.service <<EOL
[Unit]
Description=ESP32-CAM LED Monitor Service
After=network.target mosquitto.service
Wants=mosquitto.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/app.py
Restart=always
RestartSec=10

# Biztonsági beállítások
NoNewPrivileges=true
PrivateTmp=true

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=esp32cam-led-monitor

[Install]
WantedBy=multi-user.target
EOL

# Systemd újratöltése
systemctl daemon-reload

echo ""
echo -e "${GREEN}=============================================="
echo "✅ Telepítés sikeres!"
echo "==============================================${NC}"
echo ""
echo "Következő lépések:"
echo ""
echo "1. Szerkeszd a konfigurációt:"
echo "   sudo nano $INSTALL_DIR/config.json"
echo ""
echo "2. Indítsd el a service-t:"
echo "   sudo systemctl start ${SERVICE_NAME}"
echo ""
echo "3. Engedélyezd az automatikus indítást:"
echo "   sudo systemctl enable ${SERVICE_NAME}"
echo ""
echo "4. Ellenőrizd az állapotot:"
echo "   sudo systemctl status ${SERVICE_NAME}"
echo ""
echo "5. Nézd meg a log-okat:"
echo "   sudo journalctl -u ${SERVICE_NAME} -f"
echo ""
echo "6. Nyisd meg a webes felületet:"
echo "   http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo -e "${YELLOW}Fontos:${NC} A config.json fájlban állítsd be az ESP32-CAM IP címét!"
echo ""
