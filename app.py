"""
ESP32-CAM LED Monitor - Feldolgozó Alkalmazás
Home Assistant integráció MQTT-vel
"""

from flask import Flask, render_template, jsonify, request, Response
import cv2
import numpy as np
import requests
import json
import time
import threading
import paho.mqtt.client as mqtt
from datetime import datetime
import os
import logging

app = Flask(__name__)

# ===== Logging konfiguráció =====
# Flask alapértelmezett logger szintjének csökkentése
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)  # Csak WARNING és ERROR szintű üzenetek
app.logger.setLevel(logging.INFO)  # App szintű üzenetek

# ===== Konfiguráció =====
CONFIG_FILE = 'config.json'
ESP32_CAM_URL = 'http://192.168.0.67'  # ESP32-CAM IP címe
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_USER = 'M3NT1'  # Ha szükséges
MQTT_PASSWORD = 'mqttzigbeejelszo'  # Ha szükséges
MQTT_TOPIC_PREFIX = 'homeassistant/binary_sensor/led_monitor'

# ===== Globális változók =====
led_zones = []
led_states = {}
monitoring_active = False
last_image = None
last_image_time = 0
image_cache_duration = 120  # Cache 2 percig
camera_timeout = 120  # 2 perces timeout kép letöltéshez
camera_error_count = 0  # Egymás utáni hibák száma
last_error_time = 0  # Utolsó hiba időpontja
last_force_refresh_time = 0  # Utolsó force refresh időpontja
force_refresh_cooldown = 10  # Minimum 10 másodperc force refresh-ek között
mqtt_client = None
camera_lock = threading.Lock()

# ===== Konfiguráció betöltése =====
def load_config():
    global led_zones, ESP32_CAM_URL, MQTT_BROKER, MQTT_PORT, MQTT_USER, MQTT_PASSWORD
    
    # Home Assistant Add-on options ellenőrzése
    addon_options = '/data/options.json'
    if os.path.exists(addon_options):
        print("[CONFIG] Home Assistant Add-on mód detektálva")
        # Az Add-on már generálta a config.json-t a run.sh-ban
        # Itt csak ellenőrizzük
    
    # Normál config.json betöltése
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            led_zones = config.get('zones', [])
            ESP32_CAM_URL = config.get('esp32_cam_url', ESP32_CAM_URL)
            MQTT_BROKER = config.get('mqtt_broker', MQTT_BROKER)
            MQTT_PORT = config.get('mqtt_port', MQTT_PORT)
            MQTT_USER = config.get('mqtt_user', '')
            MQTT_PASSWORD = config.get('mqtt_password', '')
            print(f"[CONFIG] Betöltve {len(led_zones)} zóna")
    else:
        print(f"[CONFIG] {CONFIG_FILE} nem található, alapértelmezett értékek használata")

def save_config():
    config = {
        'zones': led_zones,
        'esp32_cam_url': ESP32_CAM_URL,
        'mqtt_broker': MQTT_BROKER,
        'mqtt_port': MQTT_PORT,
        'mqtt_user': MQTT_USER,
        'mqtt_password': MQTT_PASSWORD
    }
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print("[CONFIG] Mentve")

# ===== MQTT Kapcsolat =====
def on_mqtt_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[MQTT] Kapcsolódva: {MQTT_BROKER}:{MQTT_PORT}")
        # Auto-discovery üzenetek küldése Home Assistant számára
        publish_homeassistant_discovery()
    else:
        print(f"[MQTT] Kapcsolódási hiba: {rc}")

def on_mqtt_disconnect(client, userdata, rc):
    print(f"[MQTT] Kapcsolat megszakadt: {rc}")

def init_mqtt():
    global mqtt_client
    # Kompatibilitás paho-mqtt 1.x és 2.x verziókkal
    try:
        # paho-mqtt 2.x
        mqtt_client = mqtt.Client(
            client_id="esp32cam_led_monitor",
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )
    except (AttributeError, TypeError):
        # paho-mqtt 1.x (régebbi verzió)
        mqtt_client = mqtt.Client(client_id="esp32cam_led_monitor")
    
    mqtt_client.on_connect = on_mqtt_connect
    mqtt_client.on_disconnect = on_mqtt_disconnect
    
    if MQTT_USER and MQTT_PASSWORD:
        mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
        return True
    except Exception as e:
        print(f"[MQTT] Kapcsolódási hiba: {e}")
        return False

def publish_homeassistant_discovery():
    """Home Assistant auto-discovery konfigurációk publikálása"""
    for zone in led_zones:
        zone_id = zone['id']
        zone_name = zone['name']
        
        # Discovery config
        config_topic = f"{MQTT_TOPIC_PREFIX}/{zone_id}/config"
        state_topic = f"{MQTT_TOPIC_PREFIX}/{zone_id}/state"
        
        config_payload = {
            "name": f"Fűtés {zone_name}",
            "unique_id": f"led_monitor_{zone_id}",
            "state_topic": state_topic,
            "device_class": "heat",
            "payload_on": "ON",
            "payload_off": "OFF",
            "icon": "mdi:radiator",
            "device": {
                "identifiers": ["esp32cam_led_monitor"],
                "name": "ESP32-CAM LED Monitor",
                "model": "Computherm LED Monitor",
                "manufacturer": "Custom"
            }
        }
        
        mqtt_client.publish(config_topic, json.dumps(config_payload), retain=True)
        print(f"[MQTT] Discovery publikálva: {zone_name}")
    
    # Kezdeti állapotok publikálása (OFF vagy cache-elt érték)
    print("[MQTT] Kezdeti állapotok publikálása...")
    for zone in led_zones:
        zone_id = zone['id']
        # Ha van már tárolt állapot (pl. újraindítás után), használjuk azt
        initial_state = led_states.get(zone_id, False)
        publish_led_state(zone_id, initial_state)
        print(f"[MQTT] {zone['name']}: kezdeti állapot = {'ON' if initial_state else 'OFF'}")

def publish_led_state(zone_id, state):
    """LED állapot publikálása MQTT-n"""
    if mqtt_client and mqtt_client.is_connected():
        topic = f"{MQTT_TOPIC_PREFIX}/{zone_id}/state"
        payload = "ON" if state else "OFF"
        mqtt_client.publish(topic, payload, retain=True)

# ===== Képfeldolgozás =====
def capture_frame(force_refresh=False):
    """Kép letöltése az ESP32-CAM-ről (cache-elt) intelligens hibakezeléssel
    
    Args:
        force_refresh: Ha True, akkor új képet kér a cache ellenére
    
    Returns:
        numpy.ndarray vagy None: A kép vagy None hiba esetén
    """
    global last_image, last_image_time, camera_error_count, last_error_time
    global last_force_refresh_time
    
    current_time = time.time()
    
    # Rate limiting force_refresh-re - védelem a túlzott kérések ellen
    if force_refresh:
        time_since_last_force = current_time - last_force_refresh_time
        if last_force_refresh_time > 0 and time_since_last_force < force_refresh_cooldown:
            remaining_cooldown = force_refresh_cooldown - time_since_last_force
            print(f"[CAM] Rate limit: várj még {remaining_cooldown:.1f} másodpercet a következő friss képig")
            # Adj vissza cache-elt képet ha van
            if last_image is not None:
                return last_image.copy()
            return None
        last_force_refresh_time = current_time
    
    # Ha van friss cache-elt kép ÉS nem kényszerítünk frissítést, használjuk azt
    if not force_refresh and last_image is not None and (current_time - last_image_time) < image_cache_duration:
        return last_image.copy()
    
    # Exponential backoff: ha túl sok hiba volt, várjunk mielőtt újra próbálkozunk
    if camera_error_count > 0 and last_error_time > 0:
        # Backoff idő: 2^error_count * 30 sec (max 120 sec)
        backoff_time = min(120, (2 ** min(camera_error_count, 4)) * 30)
        time_since_error = current_time - last_error_time
        
        if time_since_error < backoff_time:
            remaining = backoff_time - time_since_error
            print(f"[CAM] Backoff: várakozás {remaining:.0f} másodperc ({camera_error_count} egymás utáni hiba)")
            # Ha van cache-elt kép, adjuk vissza azt még ha régi is
            if last_image is not None:
                return last_image.copy()
            return None
    
    # Lock használata hogy ne legyen több egyidejű kérés
    with camera_lock:
        # Újra ellenőrizzük a cache-t (más szál lehet hogy közben frissítette)
        if not force_refresh and last_image is not None and (time.time() - last_image_time) < image_cache_duration:
            return last_image.copy()
        
        print(f"[CAM] Kép letöltése ESP32-CAM-ről (timeout: {camera_timeout}s)...")
        start_time = time.time()
        
        try:
            # 2 perces timeout - ESP32-CAM lehet lassú
            response = requests.get(
                f"{ESP32_CAM_URL}/", 
                stream=True, 
                timeout=camera_timeout,
                headers={'Connection': 'close'}  # Ne tartsa nyitva a kapcsolatot
            )
            
            if response.status_code == 200:
                # Multipart stream első frame kinyerése
                bytes_data = bytes()
                max_bytes = 1024 * 150  # Max 150KB olvasás (nagyobb felbontáshoz)
                last_chunk_time = time.time()  # Utolsó chunk időpontja
                
                for chunk in response.iter_content(chunk_size=2048):
                    current_chunk_time = time.time()
                    
                    # Chunk szintű timeout ellenőrzés - 30 sec inaktivitás után timeout
                    time_since_last_chunk = current_chunk_time - last_chunk_time
                    if time_since_last_chunk > 30:
                        print(f"[CAM] Timeout: {time_since_last_chunk:.1f}s eltelt az utolsó chunk óta")
                        response.close()
                        raise requests.exceptions.Timeout("Chunk reading timeout")
                    
                    # Teljes idő ellenőrzés
                    if current_chunk_time - start_time > camera_timeout:
                        print(f"[CAM] Timeout: teljes idő ({camera_timeout}s) lejárt")
                        response.close()
                        raise requests.exceptions.Timeout("Total timeout exceeded")
                    
                    bytes_data += chunk
                    last_chunk_time = current_chunk_time  # Frissítjük az utolsó chunk idejét
                    
                    # JPEG kezdő és vég marker keresése
                    a = bytes_data.find(b'\xff\xd8')
                    b = bytes_data.find(b'\xff\xd9')
                    
                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b+2]
                        # Dekódolás
                        img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                        if img is not None:
                            elapsed = time.time() - start_time
                            print(f"[CAM] ✓ Kép sikeresen letöltve ({elapsed:.1f}s)")
                            
                            # Sikeres letöltés - reset error counter
                            camera_error_count = 0
                            last_error_time = 0
                            
                            last_image = img.copy()
                            last_image_time = time.time()
                            response.close()  # Kapcsolat lezárása
                            return img
                    
                    # Védelem túl nagy letöltés ellen
                    if len(bytes_data) > max_bytes:
                        print(f"[CAM] Max méret elérve ({max_bytes} bytes)")
                        break
                
                response.close()
                print(f"[CAM] ✗ Nem található érvényes JPEG adat a válaszban")
            else:
                print(f"[CAM] ✗ HTTP hiba: {response.status_code}")
                
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            print(f"[CAM] ✗ Timeout ({elapsed:.1f}s) - ESP32-CAM túl lassan válaszol vagy nem elérhető")
            camera_error_count += 1
            last_error_time = time.time()
            
        except requests.exceptions.ConnectionError as e:
            print(f"[CAM] ✗ Kapcsolat hiba - ESP32-CAM nem elérhető: {e}")
            camera_error_count += 1
            last_error_time = time.time()
            
        except Exception as e:
            print(f"[CAM] ✗ Váratlan hiba: {e}")
            camera_error_count += 1
            last_error_time = time.time()
    
    return None

def detect_led_brightness(image, zone):
    """LED fényerősség detektálása egy zónában többszínű támogatással"""
    # Biztonságos koordináta korrekció, hogy ne vágjunk üres ROI-t
    img_h, img_w = image.shape[:2]
    x = max(0, min(int(zone['x']), img_w))
    y = max(0, min(int(zone['y']), img_h))
    w = max(0, min(int(zone['width']), img_w - x))
    h = max(0, min(int(zone['height']), img_h - y))
    if w <= 0 or h <= 0:
        return False, 0.0
    
    # ROI kivágása
    roi = image[y:y+h, x:x+w]
    if roi.size == 0:
        return False, 0.0
    
    # LED típus/szín beállítása
    led_type = zone.get('led_type', 'auto')  # auto, red, green, blue, white, any
    
    # HSV konverzió
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    masks = []
    
    # Vörös LED detektálás
    if led_type in ['auto', 'red', 'any']:
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        masks.append(cv2.bitwise_or(mask1, mask2))
    
    # Zöld LED detektálás
    if led_type in ['green', 'any']:
        lower_green = np.array([40, 100, 100])
        upper_green = np.array([80, 255, 255])
        masks.append(cv2.inRange(hsv, lower_green, upper_green))
    
    # Kék LED detektálás
    if led_type in ['blue', 'any']:
        lower_blue = np.array([100, 100, 100])
        upper_blue = np.array([130, 255, 255])
        masks.append(cv2.inRange(hsv, lower_blue, upper_blue))
    
    # Fehér/Narancs LED detektálás
    if led_type in ['auto', 'white', 'orange', 'any']:
        _, white_mask = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
        masks.append(white_mask)
    
    # Kombinált maszk
    if masks:
        combined_mask = masks[0]
        for mask in masks[1:]:
            combined_mask = cv2.bitwise_or(combined_mask, mask)
    else:
        # Fallback: egyszerű fényerősség
        _, combined_mask = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    # Fényerősség számítása (0-255 skálán)
    brightness = np.mean(combined_mask)
    
    # Küszöbérték (állítható)
    threshold = zone.get('threshold', 30)
    is_on = brightness > threshold
    
    return is_on, brightness

def process_frame(force_publish=False):
    """Kép feldolgozása és LED állapotok frissítése
    
    Args:
        force_publish: Ha True, minden állapotot publikál MQTT-n (nem csak változásokat)
    """
    global last_image, led_states, led_zones
    
    img = capture_frame()
    if img is None:
        return False
    
    last_image = img.copy()
    
    # Minden zóna feldolgozása
    for i, zone in enumerate(led_zones):
        zone_id = zone['id']
        is_on, brightness = detect_led_brightness(img, zone)
        is_on = bool(is_on)
        
        # Állapotváltozás detektálása
        prev_state = led_states.get(zone_id, None)
        state_changed = prev_state != is_on
        
        # MQTT publikálás: változáskor VAGY force_publish esetén
        if state_changed or force_publish:
            if state_changed:
                print(f"[LED] {zone['name']}: {'BE' if is_on else 'KI'} (fényerő: {brightness:.1f})")
            publish_led_state(zone_id, is_on)
        
        # Frissítjük az állapotokat MINDKÉT helyen
        led_states[zone_id] = is_on
        led_zones[i]['last_brightness'] = float(brightness)  # JSON kompatibilis
        led_zones[i]['last_state'] = bool(is_on)
        led_zones[i]['last_check'] = datetime.now().isoformat()
    
    return True

# ===== Monitoring szál =====
def monitoring_thread():
    print("[MONITOR] Elindítva - 2 percenkénti képellenőrzés")
    cycle_count = 0
    
    while monitoring_active:
        try:
            cycle_count += 1
            print(f"[MONITOR] Ciklus #{cycle_count} - LED állapotok ellenőrzése...")
            
            # Első ciklus: minden állapotot publikálunk MQTT-n (force_publish=True)
            # Többi ciklus: csak változásokat publikálunk
            force_publish = (cycle_count == 1)
            if force_publish:
                print("[MONITOR] Első ciklus - minden zóna állapotát publikáljuk MQTT-n")
            
            success = process_frame(force_publish=force_publish)
            
            if success:
                print(f"[MONITOR] ✓ Ciklus #{cycle_count} sikeres")
            else:
                print(f"[MONITOR] ✗ Ciklus #{cycle_count} sikertelen - várjuk a következő próbálkozást")
            
            # 2 percenkénti ellenőrzés
            print(f"[MONITOR] Várakozás 120 másodperc a következő ellenőrzésig...")
            time.sleep(120)
            
        except Exception as e:
            print(f"[MONITOR] ✗ Váratlan hiba: {e}")
            time.sleep(120)  # Hiba esetén is 2 perc várakozás
            
    print("[MONITOR] Leállítva")

# ===== API Endpoints =====
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify({
        'zones': led_zones,
        'esp32_cam_url': ESP32_CAM_URL,
        'mqtt_broker': MQTT_BROKER,
        'mqtt_port': MQTT_PORT,
        'monitoring_active': monitoring_active
    })

@app.route('/api/config', methods=['POST'])
def update_config():
    global ESP32_CAM_URL, MQTT_BROKER, MQTT_PORT, MQTT_USER, MQTT_PASSWORD
    data = request.json
    
    ESP32_CAM_URL = data.get('esp32_cam_url', ESP32_CAM_URL)
    MQTT_BROKER = data.get('mqtt_broker', MQTT_BROKER)
    MQTT_PORT = data.get('mqtt_port', MQTT_PORT)
    MQTT_USER = data.get('mqtt_user', '')
    MQTT_PASSWORD = data.get('mqtt_password', '')
    
    save_config()
    return jsonify({'success': True})

@app.route('/api/zones', methods=['GET'])
def get_zones():
    """Zónák lekérése az aktuális állapotokkal"""
    # Frissítjük a zónák adatait az aktuális állapotokkal
    zones_with_state = []
    for zone in led_zones:
        zone_copy = zone.copy()
        zone_id = zone['id']
        # Ha van monitoring adat, frissítjük
        if zone_id in led_states:
            zone_copy['current_state'] = led_states[zone_id]
        zones_with_state.append(zone_copy)
    return jsonify(zones_with_state)

@app.route('/api/zones', methods=['POST'])
def save_zones():
    global led_zones
    led_zones = request.json
    save_config()
    
    # Ha MQTT aktív, frissítjük a discovery-t
    if mqtt_client and mqtt_client.is_connected():
        publish_homeassistant_discovery()
    
    return jsonify({'success': True})

@app.route('/api/zones/export', methods=['GET'])
def export_zones():
    """Zónák exportálása JSON fájlként letöltésre"""
    from flask import send_file
    import io
    
    # JSON generálása
    zones_json = json.dumps(led_zones, indent=2, ensure_ascii=False)
    
    # Fájl stream létrehozása
    buffer = io.BytesIO()
    buffer.write(zones_json.encode('utf-8'))
    buffer.seek(0)
    
    # Fájlnév időbélyeggel
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'led_zones_backup_{timestamp}.json'
    
    return send_file(
        buffer,
        mimetype='application/json',
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/zones/import', methods=['POST'])
def import_zones():
    """Zónák importálása feltöltött JSON fájlból"""
    global led_zones
    
    try:
        # Ellenőrizzük hogy van-e fájl
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Nincs fájl kiválasztva'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Üres fájlnév'}), 400
        
        # JSON betöltése és validálása
        content = file.read().decode('utf-8')
        imported_zones = json.loads(content)
        
        # Validálás: lista-e
        if not isinstance(imported_zones, list):
            return jsonify({'success': False, 'error': 'Érvénytelen formátum: nem lista'}), 400
        
        # Validálás: minden elem tartalmazza-e a szükséges mezőket
        required_fields = ['id', 'name', 'x', 'y', 'width', 'height']
        for zone in imported_zones:
            for field in required_fields:
                if field not in zone:
                    return jsonify({'success': False, 'error': f'Hiányzó mező: {field}'}), 400
        
        # Zónák frissítése
        led_zones = imported_zones
        save_config()
        
        # Ha MQTT aktív, frissítjük a discovery-t
        if mqtt_client and mqtt_client.is_connected():
            publish_homeassistant_discovery()
        
        return jsonify({
            'success': True, 
            'message': f'{len(imported_zones)} zóna sikeresen importálva',
            'zones': imported_zones
        })
        
    except json.JSONDecodeError as e:
        return jsonify({'success': False, 'error': f'Érvénytelen JSON: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Hiba: {str(e)}'}), 500

@app.route('/api/snapshot')
def get_snapshot():
    """Aktuális kép letöltése
    
    Query paraméter:
        refresh=true - Friss kép kérése a cache ellenére (zóna kalibráláshoz)
    """
    global last_image, last_image_time
    
    # Ellenőrizzük a refresh paramétert
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    
    # Új képet kérünk (force_refresh határozza meg hogy cache-ből vagy frissen)
    img = capture_frame(force_refresh=force_refresh)
    if img is None:
        # Ha nincs kép, adjunk vissza hibaüzenetet szöveges formában
        return jsonify({'error': 'ESP32-CAM nem elérhető. Ellenőrizd az IP címet és hogy be van-e kapcsolva a kamera.'}), 503
    
    # JPEG enkódolás
    _, buffer = cv2.imencode('.jpg', img)
    return Response(buffer.tobytes(), mimetype='image/jpeg')

@app.route('/api/annotated_snapshot')
def get_annotated_snapshot():
    """Kép a zónákkal kirajzolva ÉS valós idejű detektálással
    
    Query paraméter:
        refresh=true - Friss kép kérése a cache ellenére (zóna kalibráláshoz)
    """
    global last_image, last_image_time, led_states, led_zones
    
    # Ellenőrizzük a refresh paramétert
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    
    # Képet kérünk (force_refresh határozza meg hogy cache-ből vagy frissen)
    img_original = capture_frame(force_refresh=force_refresh)
    
    if img_original is None:
        return jsonify({'error': 'ESP32-CAM nem elérhető'}), 503
    
    # FONTOS: Detektálást az EREDETI, tiszta képen végezzük!
    # Rajzoláshoz készítünk egy MÁSOLATOT, hogy a keretek ne befolyásolják a következő zóna detektálását
    img_annotated = img_original.copy()
    
    # VALÓS IDEJŰ DETEKTÁLÁS minden zónára - TISZTA KÉPEN!
    # Egyedi színpaletta minden zónához (BGR formátum OpenCV-ben)
    zone_colors = [
        (255, 100, 100),   # Világoskék
        (100, 255, 100),   # Világoszöld
        (255, 150, 255),   # Rózsaszín
        (100, 255, 255),   # Sárga
        (255, 100, 255),   # Lila
        (150, 255, 150),   # Menta
        (200, 150, 100),   # Türkiz
        (100, 150, 255),   # Narancs
    ]
    
    for i, zone in enumerate(led_zones):
        zone_id = zone['id']
        # Koordináták biztonságos korrekciója
        img_h, img_w = img_original.shape[:2]
        x = max(0, min(int(zone['x']), img_w))
        y = max(0, min(int(zone['y']), img_h))
        w = max(0, min(int(zone['width']), img_w - x))
        h = max(0, min(int(zone['height']), img_h - y))
        if w <= 0 or h <= 0:
            continue
        
        # LED állapot detektálása az EREDETI képen (keretek nélkül!)
        is_on, brightness = detect_led_brightness(img_original, zone)
        is_on = bool(is_on)
        
        # Állapotok frissítése
        led_states[zone_id] = is_on
        led_zones[i]['last_brightness'] = float(brightness)
        led_zones[i]['last_state'] = bool(is_on)
        led_zones[i]['last_check'] = datetime.now().isoformat()
        
        # Egyedi szín hozzárendelése minden zónához
        base_color = zone_colors[i % len(zone_colors)]
        
        # Keret rajzolása a MÁSOLATON - vastagabb, átlátszó belső terület
        # Félig átlátszó kitöltés a zóna területére (20% átlátszatlanság)
        overlay = img_annotated.copy()
        cv2.rectangle(overlay, (x, y), (x+w, y+h), base_color, -1)
        cv2.addWeighted(overlay, 0.2, img_annotated, 0.8, 0, img_annotated)
        
        # Vastagabb keret (3px) - erősebb szín ha BE van kapcsolva
        border_color = tuple([int(c * 1.2) if is_on else int(c * 0.6) for c in base_color])
        border_thickness = 4 if is_on else 3
        cv2.rectangle(img_annotated, (x, y), (x+w, y+h), border_color, border_thickness)
    
    # BAL FELSŐ SAROKBAN: Zóna lista színes háttérrel
    list_x = 10
    list_y = 10
    line_height = 30
    list_font_scale = 0.6
    list_font_thickness = 2
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Félátlátszó fekete háttér a teljes listához
    max_text_width = 0
    for i, zone in enumerate(led_zones):
        text = f"{i+1}. {zone['name']}"
        (tw, th), _ = cv2.getTextSize(text, font, list_font_scale, list_font_thickness)
        max_text_width = max(max_text_width, tw)
    
    list_bg_overlay = img_annotated.copy()
    cv2.rectangle(list_bg_overlay,
                 (list_x - 5, list_y - 5),
                 (list_x + max_text_width + 15, list_y + len(led_zones) * line_height + 5),
                 (0, 0, 0), -1)
    cv2.addWeighted(list_bg_overlay, 0.7, img_annotated, 0.3, 0, img_annotated)
    
    # Zóna nevek felsorolása a megfelelő színekkel
    for i, zone in enumerate(led_zones):
        base_color = zone_colors[i % len(zone_colors)]
        text = f"{i+1}. {zone['name']}"
        text_y = list_y + (i + 1) * line_height - 5
        
        # Szöveg a zóna színével
        cv2.putText(img_annotated, text, (list_x, text_y),
                   font, list_font_scale, base_color, list_font_thickness)
    
    _, buffer = cv2.imencode('.jpg', img_annotated)
    return Response(buffer.tobytes(), mimetype='image/jpeg')

@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    global monitoring_active
    if not monitoring_active:
        monitoring_active = True
        thread = threading.Thread(target=monitoring_thread, daemon=True)
        thread.start()
        return jsonify({'success': True, 'message': 'Monitoring elindítva'})
    return jsonify({'success': False, 'message': 'Már fut'})

@app.route('/api/monitoring/stop', methods=['POST'])
def stop_monitoring():
    global monitoring_active
    monitoring_active = False
    return jsonify({'success': True, 'message': 'Monitoring leállítva'})

@app.route('/api/states')
def get_states():
    """Aktuális LED állapotok"""
    return jsonify(led_states)

@app.route('/api/mqtt/cleanup', methods=['POST'])
def mqtt_cleanup():
    """MQTT discovery config-ok törlése (Home Assistant entitások eltávolítása)"""
    if not mqtt_client or not mqtt_client.is_connected():
        return jsonify({'success': False, 'error': 'MQTT nem csatlakozva'}), 503
    
    try:
        deleted_count = 0
        for zone in led_zones:
            zone_id = zone['id']
            # Config topic törlése (üres payload, retain=True)
            config_topic = f"{MQTT_TOPIC_PREFIX}/{zone_id}/config"
            mqtt_client.publish(config_topic, '', retain=True)
            # State topic törlése
            state_topic = f"{MQTT_TOPIC_PREFIX}/{zone_id}/state"
            mqtt_client.publish(state_topic, '', retain=True)
            deleted_count += 1
            print(f"[MQTT] Cleanup: {zone['name']} config törölve")
        
        return jsonify({
            'success': True,
            'message': f'{deleted_count} entitás config törölve. Indítsd újra a Home Assistant-ot vagy várj ~1 percet.',
            'deleted_count': deleted_count
        })
    except Exception as e:
        print(f"[MQTT] Cleanup hiba: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/camera/health')
def camera_health():
    """ESP32-CAM kamera állapotának ellenőrzése"""
    global last_image_time, camera_error_count, last_error_time
    
    current_time = time.time()
    time_since_last_image = current_time - last_image_time if last_image_time > 0 else None
    time_since_last_error = current_time - last_error_time if last_error_time > 0 else None
    
    # Állapot meghatározása
    if last_image is None:
        status = "never_connected"
        health = "unknown"
    elif camera_error_count == 0:
        status = "healthy"
        health = "good"
    elif camera_error_count < 3:
        status = "degraded"
        health = "warning"
    else:
        status = "unhealthy"
        health = "critical"
    
    return jsonify({
        'status': status,
        'health': health,
        'last_image_age_seconds': time_since_last_image,
        'consecutive_errors': camera_error_count,
        'time_since_last_error_seconds': time_since_last_error,
        'camera_url': ESP32_CAM_URL,
        'cache_duration_seconds': image_cache_duration,
        'timeout_seconds': camera_timeout,
        'has_cached_image': last_image is not None
    })

# ===== Alkalmazás indítása =====
if __name__ == '__main__':
    print("=" * 50)
    print("ESP32-CAM LED Monitor - Feldolgozó Alkalmazás")
    print("=" * 50)
    
    # Konfiguráció betöltése
    load_config()
    
    # MQTT inicializálás
    if init_mqtt():
        print("[OK] MQTT csatlakozva")
    else:
        print("[WARN] MQTT nem elérhető")
    
    # Flask szerver indítása
    print("\nWebes felület: http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
