import requests

BASE_URL = "http://127.0.0.1:5000"
NOTES_URL = f"{BASE_URL}/notes"
AUTHORS_URL = f"{BASE_URL}/authors"

r = requests.post(NOTES_URL, json={"author": "Иван", "text": "Первая заметка Ивана"})
print(r.status_code, r.json())
note1_id = r.json().get("id")

r = requests.post(NOTES_URL, json={"author": "Анна", "text": "Заметка Анны"})
print(r.status_code, r.json())
note2_id = r.json().get("id")

r = requests.post(NOTES_URL, json={"author": "Иван", "text": "Вторая заметка Ивана"})
print(r.status_code, r.json())
note3_id = r.json().get("id")

r = requests.post(NOTES_URL, json={"text": "Заметка без автора"})
print(r.status_code, r.json())

r = requests.post(NOTES_URL, json={"author": "Петр", "text": "   "})
print(r.status_code, r.json())
print()

r = requests.get(NOTES_URL)
print(r.status_code, r.json())

r = requests.get(NOTES_URL, params={"author": "Иван", "limit": 1, "offset": 0})
print(r.status_code, r.json())

r = requests.get(NOTES_URL, params={"sort": "likes", "order": "desc"})
print(r.status_code, r.json())

r = requests.get(NOTES_URL, params={"sort": "date"})
print(r.status_code, r.json())

r = requests.get(NOTES_URL, params={"limit": "два"})
print(r.status_code, r.json())
print()

r = requests.get(f"{NOTES_URL}/{note1_id}")
print(r.status_code, r.json())

r = requests.get(f"{NOTES_URL}/999999")
print(r.status_code, r.json())
print()

r = requests.put(f"{NOTES_URL}/{note1_id}", json={"author": "Иван", "text": "Новый текст Иван"})
print(r.status_code, r.json())

r = requests.put(f"{NOTES_URL}/{note1_id}", json={"text": "Текст без автора"})
print(r.status_code, r.json())
print()

r = requests.patch(f"{NOTES_URL}/{note2_id}", json={"text": "Анна изменила текст"})
print(r.status_code, r.json())

r = requests.patch(f"{NOTES_URL}/{note2_id}", json={"author": ""})
print(r.status_code, r.json())
print()

requests.post(f"{NOTES_URL}/{note2_id}/like")
r = requests.post(f"{NOTES_URL}/{note2_id}/like")
print(r.status_code, r.json())

r = requests.post(f"{NOTES_URL}/999999/like")
print(r.status_code, r.json())
print()

r = requests.get(AUTHORS_URL)
print(r.status_code, r.json())
print()

r = requests.delete(f"{NOTES_URL}/{note3_id}")
print(r.status_code)

r = requests.delete(f"{NOTES_URL}/999999")
print(r.status_code, r.json())

r = requests.delete(NOTES_URL, params={"author": "Иван"})
print(r.status_code, r.json())

r = requests.delete(NOTES_URL, params={"author": "НеизвестныйАвтор"})
print(r.status_code, r.json())

r = requests.delete(NOTES_URL)
print(r.status_code, r.json())