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

app = Flask(__name__)

# ===== Konfiguráció =====
CONFIG_FILE = 'config.json'
ESP32_CAM_URL = 'http://192.168.10.130'  # ESP32-CAM IP címe
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_USER = ''  # Ha szükséges
MQTT_PASSWORD = ''  # Ha szükséges
MQTT_TOPIC_PREFIX = 'homeassistant/binary_sensor/led_monitor'

# ===== Globális változók =====
led_zones = []
led_states = {}
monitoring_active = False
last_image = None
last_image_time = 0
image_cache_duration = 0.5  # Cache 0.5 másodpercig
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
    mqtt_client = mqtt.Client(client_id="esp32cam_led_monitor", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
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

def publish_led_state(zone_id, state):
    """LED állapot publikálása MQTT-n"""
    if mqtt_client and mqtt_client.is_connected():
        topic = f"{MQTT_TOPIC_PREFIX}/{zone_id}/state"
        payload = "ON" if state else "OFF"
        mqtt_client.publish(topic, payload, retain=True)

# ===== Képfeldolgozás =====
def capture_frame():
    """Kép letöltése az ESP32-CAM-ről (cache-elt)"""
    global last_image, last_image_time
    
    # Ha van friss cache-elt kép, használjuk azt
    current_time = time.time()
    if last_image is not None and (current_time - last_image_time) < image_cache_duration:
        return last_image.copy()
    
    # Lock használata hogy ne legyen több egyidejű kérés
    with camera_lock:
        # Újra ellenőrizzük a cache-t (más szál lehet hogy közben frissítette)
        if last_image is not None and (time.time() - last_image_time) < image_cache_duration:
            return last_image.copy()
        
        try:
            # Próbáljuk meg rövid timeout-tal, kevesebb újrapróbálkozással
            response = requests.get(
                f"{ESP32_CAM_URL}/", 
                stream=True, 
                timeout=3,
                headers={'Connection': 'close'}  # Ne tartsa nyitva a kapcsolatot
            )
            
            if response.status_code == 200:
                # Multipart stream első frame kinyerése
                bytes_data = bytes()
                max_bytes = 1024 * 100  # Max 100KB olvasás
                
                for chunk in response.iter_content(chunk_size=2048):
                    bytes_data += chunk
                    
                    # JPEG kezdő és vég marker keresése
                    a = bytes_data.find(b'\xff\xd8')
                    b = bytes_data.find(b'\xff\xd9')
                    
                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b+2]
                        # Dekódolás
                        img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                        if img is not None:
                            last_image = img.copy()
                            last_image_time = time.time()
                            response.close()  # Kapcsolat lezárása
                            return img
                    
                    # Védelem túl nagy letöltés ellen
                    if len(bytes_data) > max_bytes:
                        break
                
                response.close()
                
        except requests.exceptions.Timeout:
            print(f"[CAM] Timeout - ESP32-CAM nem válaszol időben")
        except requests.exceptions.ConnectionError as e:
            print(f"[CAM] Kapcsolat hiba - ESP32-CAM nem elérhető")
        except Exception as e:
            print(f"[CAM] Hiba: {e}")
    
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

def process_frame():
    """Kép feldolgozása és LED állapotok frissítése"""
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
        if prev_state != is_on:
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
    print("[MONITOR] Elindítva")
    while monitoring_active:
        try:
            process_frame()
            time.sleep(2)  # 2 másodpercenként ellenőrzés
        except Exception as e:
            print(f"[MONITOR] Hiba: {e}")
            time.sleep(5)
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

@app.route('/api/snapshot')
def get_snapshot():
    """Aktuális kép letöltése"""
    global last_image, last_image_time
    
    # Ha van friss cache-elt kép, használjuk
    if last_image is not None and (time.time() - last_image_time) < 2.0:
        _, buffer = cv2.imencode('.jpg', last_image)
        return Response(buffer.tobytes(), mimetype='image/jpeg')
    
    # Különben új képet kérünk
    img = capture_frame()
    if img is None:
        # Ha nincs kép, adjunk vissza hibaüzenetet szöveges formában
        return jsonify({'error': 'ESP32-CAM nem elérhető. Ellenőrizd az IP címet és hogy be van-e kapcsolva a kamera.'}), 503
    
    # JPEG enkódolás
    _, buffer = cv2.imencode('.jpg', img)
    return Response(buffer.tobytes(), mimetype='image/jpeg')

@app.route('/api/annotated_snapshot')
def get_annotated_snapshot():
    """Kép a zónákkal kirajzolva ÉS valós idejű detektálással"""
    global last_image, last_image_time, led_states, led_zones
    
    # Ha van friss cache-elt kép és vannak zónák
    if last_image is not None and (time.time() - last_image_time) < 2.0 and len(led_zones) > 0:
        img = last_image.copy()
    else:
        img = capture_frame()
    
    if img is None:
        return jsonify({'error': 'ESP32-CAM nem elérhető'}), 503
    
    # VALÓS IDEJŰ DETEKTÁLÁS minden zónára
    for i, zone in enumerate(led_zones):
        zone_id = zone['id']
        # Koordináták biztonságos korrekciója
        img_h, img_w = img.shape[:2]
        x = max(0, min(int(zone['x']), img_w))
        y = max(0, min(int(zone['y']), img_h))
        w = max(0, min(int(zone['width']), img_w - x))
        h = max(0, min(int(zone['height']), img_h - y))
        if w <= 0 or h <= 0:
            continue
        
        # LED állapot detektálása
        is_on, brightness = detect_led_brightness(img, zone)
        is_on = bool(is_on)
        
        # Állapotok frissítése
        led_states[zone_id] = is_on
        led_zones[i]['last_brightness'] = float(brightness)
        led_zones[i]['last_state'] = bool(is_on)
        led_zones[i]['last_check'] = datetime.now().isoformat()
        
        # Keret rajzolása a detektált állapot szerint
        color = (0, 255, 0) if is_on else (0, 0, 255)
        cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
        cv2.putText(img, zone['name'], (x, y-5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    _, buffer = cv2.imencode('.jpg', img)
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
