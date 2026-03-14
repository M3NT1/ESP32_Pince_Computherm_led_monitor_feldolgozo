from flask import Flask, Response, request
import time
import argparse
import os

app = Flask(__name__)

# Állapot változók
is_streaming = False
last_request_time = 0
RATE_LIMIT_MS = 2000

# Szimulált dummy kép (készítsünk egy kicsi sötét képet, ha nincs jobb)
DUMMY_IMAGE_PATH = "dummy_image.jpg"
def get_dummy_image():
    if os.path.exists(DUMMY_IMAGE_PATH):
        with open(DUMMY_IMAGE_PATH, 'rb') as f:
            return f.read()
    else:
        # Ha nincs fizikai fájl, egy nagyon alap pici szürke jpeg-et adunk vissza bytestringként
        import numpy as np
        import cv2
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img[:] = (100, 100, 100) # Szürke
        cv2.putText(img, "DUMMY ESP32", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(img, f"Time: {time.time()}", (150, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        if is_streaming:
            cv2.putText(img, "STREAM ACTIVE", (200, 320), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        ret, buffer = cv2.imencode('.jpg', img)
        return buffer.tobytes()

@app.route('/set_streaming', methods=['POST'])
def set_streaming():
    global is_streaming
    state = request.json.get('active', False)
    is_streaming = state
    return {"success": True, "streaming": is_streaming}

@app.route('/capture') # Custom Arduino Endpoint
def capture_custom():
    global last_request_time
    now = time.time() * 1000
    
    # 1. Rate Limiting Check
    if (now - last_request_time) < RATE_LIMIT_MS:
        last_request_time = now
        time.sleep(0.5)
        return "Too Many Requests", 429
        
    last_request_time = now

    # 2. Stream Lock Check
    if is_streaming:
        return "Kamera mar hasznalatban", 500

    # 3. Kép küldése
    return Response(get_dummy_image(), mimetype='image/jpeg', headers={"Connection": "close"})

@app.route('/') # ESPHome Endpoint
def capture_esphome():
    # ESPHome nem feltétlenül rate limitál olyan szigorúan gyárilag, 
    # de a dummy-ban szimulálhatjuk a nyers kép visszaadását.
    return Response(get_dummy_image(), mimetype='image/jpeg', headers={"Connection": "close"})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dummy ESP32-CAM Server')
    parser.add_argument('--port', type=int, default=80, help='Port to run the server on (default: 80)')
    parser.add_argument('--streaming', action='store_true', help='Start with streaming mode active')
    args = parser.parse_args()

    is_streaming = args.streaming

    print(f"Indul a Dummy ESP32 Server a {args.port}-es porton.")
    print(f"Jelenlegi Stream Mode: {'AKTÍV (500-as hibát dob /capture-re)' if is_streaming else 'INAKTÍV'}")
    print("Végpontok:")
    print(f"  - http://127.0.0.1:{args.port}/capture  (Custom Arduino logikát szimulál)")
    print(f"  - http://127.0.0.1:{args.port}/         (ESPHome logikát szimulál)")
    print("A stream mód átkapcsolható futás közben: POST /set_streaming (json payload: {'active': true/false})")
    print("-" * 50)
    
    app.run(host='0.0.0.0', port=args.port, debug=False)
