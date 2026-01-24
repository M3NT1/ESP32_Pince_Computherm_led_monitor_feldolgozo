# Raspberry Pi 4 Gyors Referencia

## 🚀 Gyors Parancsok

### Telepítés
```bash
sudo ./install_rpi.sh
```

### Service Kezelés
```bash
sudo systemctl start esp32cam-led-monitor      # Indítás
sudo systemctl stop esp32cam-led-monitor       # Leállítás
sudo systemctl restart esp32cam-led-monitor    # Újraindítás
sudo systemctl status esp32cam-led-monitor     # Állapot
sudo systemctl enable esp32cam-led-monitor     # Auto-start BE
sudo systemctl disable esp32cam-led-monitor    # Auto-start KI
```

### Log-ok
```bash
sudo journalctl -u esp32cam-led-monitor -f     # Élő log
sudo journalctl -u esp32cam-led-monitor -n 50  # Utolsó 50 sor
sudo journalctl -u esp32cam-led-monitor --since today  # Mai log-ok
```

### Konfiguráció
```bash
sudo nano /opt/esp32cam_led_monitor/config.json
```

### Webes Felület
```
http://[RASPBERRY_PI_IP]:5000
```

### IP Cím Lekérdezése
```bash
hostname -I
```

### MQTT Tesztelés
```bash
mosquitto_sub -h localhost -t "homeassistant/#" -v
```

## 📍 Fontos Helyek

- **Alkalmazás**: `/opt/esp32cam_led_monitor/`
- **Service fájl**: `/etc/systemd/system/esp32cam-led-monitor.service`
- **Config**: `/opt/esp32cam_led_monitor/config.json`
- **Python venv**: `/opt/esp32cam_led_monitor/venv/`

## 🐛 Gyors Hibaelhárítás

### Service nem indul
```bash
sudo systemctl status esp32cam-led-monitor -l
cd /opt/esp32cam_led_monitor
source venv/bin/activate
python3 app.py
```

### MQTT probléma
```bash
sudo systemctl status mosquitto
sudo systemctl restart mosquitto
```

### ESP32-CAM nem elérhető
```bash
ping [ESP32_CAM_IP]
curl http://[ESP32_CAM_IP]/
```

## 🔧 Konfigurációs Példa

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

## 📊 Monitoring

### Rendszer erőforrások
```bash
htop                    # CPU/RAM
df -h                   # Tárhely
vcgencmd measure_temp   # Hőmérséklet
```

### Hálózat
```bash
ifconfig               # IP címek
netstat -tuln | grep 5000   # Port ellenőrzés
```

## 🔄 Frissítés

```bash
sudo systemctl stop esp32cam-led-monitor
cd /opt/esp32cam_led_monitor
# Új fájlok másolása ide
sudo systemctl start esp32cam-led-monitor
```
