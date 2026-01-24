# 🍓 Raspberry Pi 4 Telepítési Útmutató
## ESP32-CAM LED Monitor Home Assistant integrációval

Ez az útmutató segít telepíteni az ESP32-CAM LED Monitor alkalmazást Raspberry Pi 4-re, ahol a Home Assistant is fut.

## 📋 Előfeltételek

- **Raspberry Pi 4** (2GB+ RAM ajánlott)
- **Raspberry Pi OS** (Bullseye vagy újabb)
- **Home Assistant** telepítve és fut
- **MQTT Broker** (Mosquitto) fut a Raspberry Pi-n
- **Hálózati kapcsolat** az ESP32-CAM és a Raspberry Pi között
- **SSH hozzáférés** a Raspberry Pi-hez

## 🚀 Gyors Telepítés

### 1. Fájlok másolása Raspberry Pi-re

```bash
# Helyi gépről (Mac/Linux)
scp -r Home_assistant_kiegeszito_feldolgozo pi@[RASPBERRY_PI_IP]:/home/pi/

# Vagy használj WinSCP-t Windows-on
```

### 2. SSH Csatlakozás

```bash
ssh pi@[RASPBERRY_PI_IP]
```

### 3. Telepítő Script Futtatása

```bash
cd /home/pi/Home_assistant_kiegeszito_feldolgozo
chmod +x install_rpi.sh
sudo ./install_rpi.sh
```

A telepítés **5-10 percet** vesz igénybe (függőségek letöltése).

### 4. Konfiguráció

```bash
sudo nano /opt/esp32cam_led_monitor/config.json
```

Minimális konfiguráció:
```json
{
  "zones": [],
  "esp32_cam_url": "http://192.168.1.100",
  "mqtt_broker": "localhost",
  "mqtt_port": 1883,
  "mqtt_user": "",
  "mqtt_password": ""
}
```

### 5. Service Indítása

```bash
# Service indítása
sudo systemctl start esp32cam-led-monitor

# Automatikus indítás engedélyezése
sudo systemctl enable esp32cam-led-monitor

# Állapot ellenőrzése
sudo systemctl status esp32cam-led-monitor
```

### 6. Webes Felület Elérése

Nyisd meg böngészőben:
```
http://[RASPBERRY_PI_IP]:5000
```

Például: `http://192.168.1.50:5000`

## 🔧 Systemd Service Kezelése

### Service parancsok

```bash
# Indítás
sudo systemctl start esp32cam-led-monitor

# Leállítás
sudo systemctl stop esp32cam-led-monitor

# Újraindítás
sudo systemctl restart esp32cam-led-monitor

# Állapot
sudo systemctl status esp32cam-led-monitor

# Automatikus indítás engedélyezése
sudo systemctl enable esp32cam-led-monitor

# Automatikus indítás tiltása
sudo systemctl disable esp32cam-led-monitor
```

### Log-ok megtekintése

```bash
# Élő log követés
sudo journalctl -u esp32cam-led-monitor -f

# Utolsó 50 sor
sudo journalctl -u esp32cam-led-monitor -n 50

# Mai log-ok
sudo journalctl -u esp32cam-led-monitor --since today

# Hibák
sudo journalctl -u esp32cam-led-monitor -p err
```

## 🐛 Hibaelhárítás

### Service nem indul

```bash
# Részletes állapot
sudo systemctl status esp32cam-led-monitor -l

# Kézi indítás teszteléshez
cd /opt/esp32cam_led_monitor
source venv/bin/activate
python3 app.py
```

### Port már használatban (5000)

Ha más alkalmazás használja az 5000-es portot, módosítsd az [app.py](app.py) utolsó sorát:

```python
app.run(host='0.0.0.0', port=5001, debug=False)  # 5001-re változtatva
```

Majd:
```bash
sudo systemctl restart esp32cam-led-monitor
```

### MQTT kapcsolat nem működik

```bash
# Mosquitto állapot
sudo systemctl status mosquitto

# MQTT tesztelés
mosquitto_sub -h localhost -t "homeassistant/#" -v

# Ha nem telepített Mosquitto
sudo apt-get install mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

### OpenCV hiba (libGL error)

Ez normális headless rendszeren. Az alkalmazás használja az `opencv-python-headless` csomagot ami nem igényel GUI-t.

### ESP32-CAM nem elérhető

```bash
# Ping tesztelés
ping [ESP32_CAM_IP]

# Böngészőből tesztelés
curl http://[ESP32_CAM_IP]/
```

## ⚡ Teljesítmény Optimalizálás

### Raspberry Pi 4 Beállítások

```bash
# GPU memória növelése (ha szükséges)
sudo nano /boot/config.txt
# Adj hozzá: gpu_mem=128

# CPU governor performance módra
sudo apt-get install cpufrequtils
echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils
sudo systemctl restart cpufrequtils
```

### Memória használat csökkentése

Az [app.py](app.py) fájlban:

```python
# Monitoring gyakoriság növelése (kevesebb CPU)
time.sleep(5)  # 2-ről 5-re

# Kamera felbontás csökkentése ESP32-CAM-en
config.frame_size = FRAMESIZE_QVGA;  // 320×240 (VGA helyett)
```

## 🔐 Biztonság

### Firewall beállítás (opcionális)

```bash
sudo apt-get install ufw
sudo ufw allow 5000/tcp
sudo ufw allow from 192.168.1.0/24 to any port 5000
sudo ufw enable
```

### MQTT hitelesítés

```bash
# Mosquitto felhasználó létrehozása
sudo mosquitto_passwd -c /etc/mosquitto/passwd esp32cam

# Mosquitto konfiguráció
sudo nano /etc/mosquitto/mosquitto.conf
# Adj hozzá:
# allow_anonymous false
# password_file /etc/mosquitto/passwd

sudo systemctl restart mosquitto
```

Frissítsd a `config.json`-t:
```json
{
  "mqtt_user": "esp32cam",
  "mqtt_password": "your_password"
}
```

## 📊 Erőforrás Használat

Raspberry Pi 4 (4GB RAM):
- **RAM**: ~150MB
- **CPU**: 5-15% (monitoring közben)
- **Tárhely**: ~500MB (virtuális környezettel)

## 🔄 Frissítés

```bash
cd /opt/esp32cam_led_monitor

# Service leállítása
sudo systemctl stop esp32cam-led-monitor

# Új fájlok másolása
# (SCP-vel vagy git pull)

# Virtuális környezet aktiválása
source venv/bin/activate

# Függőségek frissítése
pip install --upgrade -r requirements.txt

# Service indítása
sudo systemctl start esp32cam-led-monitor
```

## 🗑️ Eltávolítás

```bash
# Service leállítása és eltávolítása
sudo systemctl stop esp32cam-led-monitor
sudo systemctl disable esp32cam-led-monitor
sudo rm /etc/systemd/system/esp32cam-led-monitor.service
sudo systemctl daemon-reload

# Fájlok törlése
sudo rm -rf /opt/esp32cam_led_monitor
```

## 📱 Home Assistant Integráció

A Raspberry Pi-n futó MQTT broker miatt a Home Assistant **azonnal** látni fogja az eszközöket.

Ellenőrzés:
1. Home Assistant → Settings → Devices & Services → MQTT
2. Keress rá: "ESP32-CAM LED Monitor"
3. Az entitások láthatók: `binary_sensor.futes_*`

## 🌐 Hálózati Hozzáférés

Ha más eszközökről is el szeretnéd érni:

```bash
# Port forwarding router-en (opcionális)
External: 5000 → Internal: [RASPBERRY_PI_IP]:5000
```

Vagy használj **Home Assistant ingress** funkciót (haladó).

## 📞 Támogatás

Probléma esetén:

1. Ellenőrizd a log-okat: `sudo journalctl -u esp32cam-led-monitor -f`
2. Systemd állapot: `sudo systemctl status esp32cam-led-monitor`
3. MQTT kapcsolat: `mosquitto_sub -h localhost -t "homeassistant/#" -v`
4. Hálózat: `ping [ESP32_CAM_IP]`

---

**Raspberry Pi 4 optimalizálva** 🍓  
**Utolsó frissítés**: 2026. január 24.
