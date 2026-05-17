import requests
import json

sid = 'mock-session-bugtest2'

# Test 1: Init
r1 = requests.post('http://localhost:8000/api/chat/message', json={'sessionId': sid, 'message': '__INIT__'})
print('=== INIT ===')
print('Stage:', r1.json()['stage'])

# Test 2: Just "hi"
r2 = requests.post('http://localhost:8000/api/chat/message', json={'sessionId': sid, 'message': 'hi'})
print('\n=== After "hi" ===')
print('Stage:', r2.json()['stage'])
print('Reply:', r2.json()['reply'][:100])

# Test 3: Issue + location only
r3 = requests.post('http://localhost:8000/api/chat/message', json={'sessionId': sid, 'message': 'My phone was stolen in Bangalore'})
print('\n=== After issue + location ===')
print('Stage:', r3.json()['stage'])
print('Facts:', json.dumps(r3.json()['extractedFacts'], indent=2))

# Test 4: Add amount
r4 = requests.post('http://localhost:8000/api/chat/message', json={'sessionId': sid, 'message': '50000 rupees'})
print('\n=== After adding amount ===')
print('Stage:', r4.json()['stage'])
print('Facts:', json.dumps(r4.json()['extractedFacts'], indent=2))

# Test 5: Add date with better format
r5 = requests.post('http://localhost:8000/api/chat/message', json={'sessionId': sid, 'message': 'It happened 2 days ago'})
print('\n=== After adding date (2 days ago) ===')
print('Stage:', r5.json()['stage'])
print('Facts:', json.dumps(r5.json()['extractedFacts'], indent=2))
print('Should be analysis now:', r5.json()['stage'] == 'analysis')

# Made with Bob
