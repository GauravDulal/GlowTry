import urllib.request
import urllib.parse
import json
import os

# Create a multipart/form-data payload without external libraries
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'

# 1. Image part
with open('../test_face_v2.png', 'rb') as f:
    img_data = f.read()

part_img_head = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="image"; filename="test_face.jpg"\r\n'
    f'Content-Type: image/jpeg\r\n\r\n'
).encode('utf-8')

# 2. Config part
config = {
    "lipstick": {"enabled": True, "color": [200, 50, 50], "intensity": 0.6},
    "blush": {"enabled": True, "color": [255, 105, 180], "intensity": 0.5},
    "eyeshadow": {"enabled": True, "color": [150, 100, 200], "intensity": 0.4},
    "eyeliner": {"enabled": True, "color": [0, 0, 0], "intensity": 0.7, "thickness": 3}
}
config_str = json.dumps(config)

part_config = (
    f'\r\n--{boundary}\r\n'
    f'Content-Disposition: form-data; name="config"\r\n\r\n'
    f'{config_str}\r\n'
    f'--{boundary}--\r\n'
).encode('utf-8')

# Construct the full body
body = part_img_head + img_data + part_config

req = urllib.request.Request('http://localhost:8000/apply-makeup', data=body, method='POST')
req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
req.add_header('Content-Length', str(len(body)))

try:
    with urllib.request.urlopen(req) as res:
        response_data = json.loads(res.read().decode('utf-8'))
        
        if "error" in response_data:
            print(f"FAILED (No face detected): {response_data['error']}")
        elif "image" in response_data:
            img_b64 = response_data["image"]
            print(f"SUCCESS! Output length: {len(img_b64)}")
            print(f"Prefix: {img_b64[:30]}...")
            
            # Save it so we can be sure it's valid
            import base64
            # Backend now returns raw base64, no prefix to split
            img_raw = base64.b64decode(img_b64)
            with open("output.png", "wb") as out:
                out.write(img_raw)
            print("Wrote output to output.png - test successful!")
        else:
            print("FAILED (Unknown format)")
except Exception as e:
    print(f"FAILED (Server error): {e}")

