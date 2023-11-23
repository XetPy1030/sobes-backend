import requests


resp = requests.post("http://localhost:5000/todo/", json={
    "username": "test",
    "email": "test@test.test",
    "text": "test",
})

print(resp.text, resp.status_code)
