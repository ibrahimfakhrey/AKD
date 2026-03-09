import urllib.request
import json
import uuid

# 1. Login
data = json.dumps({'email': 'user@test.com', 'password': 'test1234'}).encode('utf-8')
req = urllib.request.Request('http://localhost:5000/api/v1/auth/login', data=data, headers={'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req)
result = json.loads(resp.read().decode('utf-8'))
token = result.get('access_token')

# 2. Assign active challenge
payload = json.dumps({'friend_email': 'admin@akd.app', 'description': 'Dummy Challenge'}).encode('utf-8')
req2 = urllib.request.Request('http://localhost:5000/api/v1/challenges/send', data=payload, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})
try:
    resp2 = urllib.request.urlopen(req2)
    challenge = json.loads(resp2.read().decode('utf-8'))
    print("Sent challenge:", challenge)
except Exception as e:
    print("Error sending challenge:", e)

# 3. Login as admin
data = json.dumps({'email': 'admin@akd.app', 'password': 'admin123'}).encode('utf-8')
req = urllib.request.Request('http://localhost:5000/api/v1/auth/login', data=data, headers={'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req)
result = json.loads(resp.read().decode('utf-8'))
admin_token = result.get('access_token')

# 4. Get active challenge
req3 = urllib.request.Request('http://localhost:5000/api/v1/challenges/active', headers={'Authorization': f'Bearer {admin_token}'})
try:
    resp3 = urllib.request.urlopen(req3)
    active = json.loads(resp3.read().decode('utf-8'))
    print("Active challenge:", active)
    if active:
        cid = active['id']
        
        # 5. Submit proof (multipart/form-data manually)
        boundary = uuid.uuid4().hex
        body = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="photo"; filename="test.png"\r\n'
            f'Content-Type: image/png\r\n\r\n'
            f'dummy file content\r\n'
            f'--{boundary}--\r\n'
        ).encode('utf-8')
        
        req4 = urllib.request.Request(f'http://localhost:5000/api/v1/challenges/{cid}/submit', data=body, headers={'Authorization': f'Bearer {admin_token}', 'Content-Type': f'multipart/form-data; boundary={boundary}'})
        resp4 = urllib.request.urlopen(req4)
        print("Submit proof:", resp4.status, resp4.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("HTTPError:", e.code, e.read().decode('utf-8'))
