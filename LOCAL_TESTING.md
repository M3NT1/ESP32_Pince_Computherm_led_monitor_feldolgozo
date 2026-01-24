# 🧪 Helyi Tesztelési Útmutató
## Kipróbálás Home Assistant nélkül (Mac/Linux/Windows)

Ez az útmutató segít helyben kipróbálni az alkalmazást, **mielőtt a Raspberry Pi-re telepítenéd**.

## ⚡ Gyors Start (Mac/Linux)

### 1. Automatikus Telepítés

```bash
cd Home_assistant_kiegeszito_feldolgozo
chmod +x setup_local_test.sh
./setup_local_test.sh
```

### 2. Alkalmazás Indítása

```bash
# Virtuális környezet aktiválása
source venv/bin/activate

# Alkalmazás futtatása
python3 app.py
```

### 3. Böngészőben Megnyitás

```
http://localhost:5000
```

## 🪟 Windows Telepítés

### PowerShell-ben:

```powershell
# Virtuális környezet létrehozása
python -m venv venv

# Aktiválás
.\venv\Scripts\Activate.ps1

# Függőségek telepítése
pip install -r requirements.txt

# Alkalmazás indítása
python app.py
```

Ha PowerShell execution policy hibát kapsz:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 🎯 Mit Tudsz Tesztelni?

### ✅ MQTT Nélkül is Működik:

1. **Webes Felület** - Teljes funkciókészlet
2. **ESP32-CAM Csatlakozás** - Kép letöltés és megjelenítés
3. **Zóna Kijelölés** - LED területek megrajzolása
4. **LED Detektálás** - Képfeldolgozás tesztelése
5. **Monitoring** - Valós idejű állapot követés
6. **Konfiguráció** - Beállítások mentése

### ⚠️ Nem Működik (MQTT Hiányában):

- Home Assistant integráció
- MQTT üzenetek küldése
- Auto-discovery funkció

**De:** Az MQTT kapcsolat hiánya **nem akadályozza** a tesztelést! Az alkalmazás figyelmeztetést ad, de tovább fut.

## 🔧 Tesztelési Forgatókönyvek

### 1. ESP32-CAM Tesztelés (Alap)

**Előfeltétel:** ESP32-CAM fut a hálózaton

```bash
# Alkalmazás indítása
source venv/bin/activate
python3 app.py
```

**Lépések:**
1. Nyisd meg: `http://localhost:5000`
2. ⚙️ Beállítás → ESP32-CAM IP beállítása (pl: `http://192.168.10.130`)
3. 💾 Konfiguráció mentése
4. 📍 Zónák → 📷 Kép betöltése
5. Ellenőrizd, hogy látod-e a képet

✅ **Siker:** Ha látod a kamerát, akkor a kapcsolat működik!

### 2. Zóna Kijelölés Tesztelés

**Lépések:**
1. 📍 Zónák fül
2. 📷 Kép betöltése
3. Rajzolj egy négyzetet az egérrel egy LED-re
4. Nevezd el (pl: "Teszt Zóna")
5. 💾 Zónák mentése
6. Ellenőrizd, hogy megjelenik-e a listában

✅ **Siker:** A zóna kártya megjelenik a koordinátákkal

### 3. LED Detektálás Tesztelés

**Lépések:**
1. Jelölj ki 1-2 zónát (LED területek)
2. 📊 Monitoring fül
3. ▶️ Indítás
4. Figyeld a zóna kártyákat:
   - Zöld indikátor = LED világít
   - Piros indikátor = LED nem világít
5. Kapcsold be/ki a LED-et a termosztáton
6. Ellenőrizd, hogy változik-e az állapot

✅ **Siker:** Az állapot változások láthatók 2 másodpercen belül

### 4. Küszöbérték Finomhangolás

Ha a detektálás nem pontos:

**Lépések:**
1. 📍 Zónák fül
2. Állítsd a küszöböt:
   - **Túl érzékeny?** → Növeld (35-40)
   - **Nem elég érzékeny?** → Csökkentsd (20-25)
3. 💾 Zónák mentése
4. 📊 Monitoring → ▶️ Indítás
5. Teszteld újra

### 5. Teljesítmény Tesztelés

**Terminálban figyeld:**
```bash
# CPU/Memória használat (Mac)
top -pid $(pgrep -f "python3 app.py")

# Linux
htop
```

**Ellenőrizd:**
- RAM: ~150-200MB
- CPU: 5-15% monitoring közben
- FPS: Konzolban látható a frame/sec érték

## 🐛 Gyakori Problémák Teszteléskor

### Probléma 1: "ModuleNotFoundError: No module named 'flask'"

**Megoldás:**
```bash
# Virtuális környezet aktiválása
source venv/bin/activate  # Mac/Linux
.\venv\Scripts\Activate.ps1  # Windows

# Függőségek újratelepítése
pip install -r requirements.txt
```

### Probléma 2: "Nem sikerült képet letölteni"

**Ellenőrzések:**
1. ESP32-CAM be van kapcsolva?
   ```bash
   ping 192.168.10.130
   ```

2. Böngészőből elérhető?
   ```
   http://192.168.10.130/
   ```

3. IP cím helyes a webes felületen?

### Probléma 3: "[MQTT] Kapcsolódási hiba"

**Ez normális teszteléskor!** Az alkalmazás tovább fut.

Ha mégis tesztelni szeretnéd MQTT-vel:
```bash
# Docker Mosquitto (Mac/Linux)
docker run -d -p 1883:1883 --name mosquitto eclipse-mosquitto

# Vagy Homebrew (Mac)
brew install mosquitto
brew services start mosquitto
```

### Probléma 4: "Port already in use (5000)"

**Megoldás 1:** Állíts másik portot az `app.py` végén:
```python
app.run(host='0.0.0.0', port=5001, debug=False)
```

**Megoldás 2:** Állítsd le a másik alkalmazást:
```bash
# Mac - Ki használja az 5000-es portot?
lsof -i :5000

# Leállítás (PID alapján)
kill -9 [PID]
```

### Probléma 5: OpenCV hiba Mac-en

```bash
# Ha hiányzik: "No module named 'cv2'"
pip install opencv-python-headless
```

## 📊 Debug Mód

Ha részletesebb log-okat szeretnél:

**app.py módosítása:**
```python
# Utolsó sor:
app.run(host='0.0.0.0', port=5000, debug=True)  # debug=True
```

Ekkor látni fogod:
- Részletes HTTP kéréseket
- Python stack trace-eket
- Auto-reload kód módosításkor

## 🧹 Tiszta Újraindítás

Ha valamit elrontottál:

```bash
# Virtuális környezet törlése
rm -rf venv

# Config törlése
rm config.json

# Újratelepítés
./setup_local_test.sh
```

## 📸 Teszt Képek (ESP32-CAM Nélkül)

Ha nincs kéznél ESP32-CAM, használhatsz teszt képet:

**app.py módosítása teszteléshez:**
```python
def capture_frame():
    """TESZT: Statikus kép használata"""
    # Töltsd le a képet a hálózatról helyett
    img = cv2.imread('test_image.jpg')
    return img
```

Készíts egy `test_image.jpg` fájlt LED-es képpel a könyvtárban.

## ✅ Sikeres Teszt Checklist

Mielőtt Raspberry Pi-re telepítenéd, ellenőrizd:

- [ ] Alkalmazás elindul hiba nélkül
- [ ] Webes felület betölt (http://localhost:5000)
- [ ] ESP32-CAM képe látható
- [ ] Zónákat tudod rajzolni és menteni
- [ ] Monitoring elindítható
- [ ] LED állapotok helyesen detektálódnak
- [ ] Küszöbérték állítással finomhangolható
- [ ] Konfiguráció mentése működik
- [ ] CPU/RAM használat elfogadható

## 🚀 Ha Minden Működik

**Következő lépés:** Raspberry Pi telepítés!

```bash
# Fájlok másolása Raspberry Pi-re
scp -r Home_assistant_kiegeszito_feldolgozo pi@[RASPBERRY_PI_IP]:/home/pi/

# SSH és telepítés
ssh pi@[RASPBERRY_PI_IP]
cd /home/pi/Home_assistant_kiegeszito_feldolgozo
chmod +x install_rpi.sh
sudo ./install_rpi.sh
```

Lásd: [RASPBERRY_PI_INSTALL.md](RASPBERRY_PI_INSTALL.md)

## 🆘 Támogatás

Ha elakadtál:

1. Ellenőrizd a konzol kimenetét (hibák)
2. Böngésző Console (F12 → Console)
3. Python traceback elemzése
4. Config.json helyes formátum?

---

**Helyi tesztelésre optimalizálva** 🧪  
**Utolsó frissítés**: 2026. január 24.
