# 🚀 Gyors Telepítési Útmutató

## HACS Telepítés - 5 Perc

### 1️⃣ Custom Repository Hozzáadása (1 perc)

```
HACS → ⋮ → Custom repositories

Repository: https://github.com/M3NT1/ESP32_Pince_Computherm_led_monitor_feldolgozo
Category: Add-on
```

### 2️⃣ Add-on Telepítése (2 perc)

```
Settings → Add-ons → Add-on Store
Keresés: "ESP32-CAM LED Monitor"
Install → Várj
```

### 3️⃣ Konfiguráció (1 perc)

```yaml
esp32_cam_url: "http://192.168.10.130"
mqtt_broker: "core-mosquitto"
mqtt_port: 1883
```

Save → Start → Check logs

### 4️⃣ Zónák Beállítása (1 perc)

```
Böngésző: http://[HA-IP]:5001
Zónák szerkesztése → Rajzold ki a LED területeket → Mentés
```

### 5️⃣ Monitoring Indítása

```
Monitoring → Indítás
Home Assistant → Devices → ESP32-CAM LED Monitor ✅
```

---

## ✨ Mit Kapsz?

- 🔴 Valós idejű LED állapot monitor
- 🏠 Automatikus Home Assistant entitások
- 📊 Webes konfiguráló felület
- 🔄 MQTT integráció
- 📈 Grafikon és history támogatás

---

## 🆘 Probléma?

**ESP32-CAM nem elérhető?**
- Ellenőrizd az IP címet
- Pingeld: `ping 192.168.10.130`

**MQTT hiba?**
- Ellenőrizd: Settings → Add-ons → Mosquitto broker
- Legyen: Started + Auto-start ON

**Entitások nem jelennek meg?**
- Developer Tools → Services → `mqtt.reload`
- Restart Home Assistant

---

## 📚 További Információ

- 📖 [README.md](README.md) - Teljes leírás
- 📄 [DOCS.md](DOCS.md) - Részletes konfiguráció
- 🔧 [HACS_INSTALL.md](HACS_INSTALL.md) - Telepítési útmutató
- 🏠 [HOME_ASSISTANT_CONFIG.md](HOME_ASSISTANT_CONFIG.md) - HA példák

---

**GitHub:** https://github.com/M3NT1/ESP32_Pince_Computherm_led_monitor_feldolgozo
