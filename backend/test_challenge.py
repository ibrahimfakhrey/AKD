import urllib.request
import json

# 1. Login
data = json.dumps({'email': 'admin@akd.app', 'password': 'admin123'}).encode('utf-8')
req = urllib.request.Request('http://localhost:5000/api/v1/auth/login', data=data, headers={'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req)
result = json.loads(resp.read().decode('utf-8'))
token = result.get('access_token')
print("Login token:", token[:10] + '...')

# 2. Create hard challenge
payload = json.dumps({
    'title': 'Another Hard Challenge',
    'description': 'Description',
    'category': 'community',
    'difficulty_hint': 'hard',
    'reward_points': 60
}).encode('utf-8')
req2 = urllib.request.Request('http://localhost:5000/api/v1/admin/quests', data=payload, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})
try:
    resp2 = urllib.request.urlopen(req2)
    print("Create challenge status:", resp2.status)
    print("Create challenge response:", json.loads(resp2.read().decode('utf-8')))
except urllib.error.HTTPError as e:
    print("Error status:", e.code)
    print("Error response:", e.read().decode('utf-8'))
