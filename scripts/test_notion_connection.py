import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

print(f"Token: {NOTION_TOKEN[:20]}..." if NOTION_TOKEN else "❌ Token is None!")
print(f"Database ID: {NOTION_DATABASE_ID}")
print(f"Database ID length: {len(NOTION_DATABASE_ID) if NOTION_DATABASE_ID else 0}")

headers = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Notion-Version': '2025-09-03',
    'Content-Type': 'application/json'
}

url = f'https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}'

print(f"\nURL: {url}")
print(f"\nHeaders: {headers}")

try:
    response = requests.get(url, headers=headers)
    print(f"\n✅ Success! Status: {response.status_code}")
    print(response.json())
except Exception as e:
    print(f"\n❌ Error: {e}")
    if hasattr(e, 'response'):
        print(f"Response: {e.response.text}")
