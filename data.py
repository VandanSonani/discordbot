import os
import json
import requests
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

apiKey = os.getenv('BOT_API_KEY')
apiHeaderKey = 'x-api-key'

universe_id = '8497594360'
data_store_name = 'Pre-Production'
base_url = 'https://apis.roblox.com/cloud/v2/'


def get_entry_by_userid(universe, data_store, user_id, scope='global'):
    encoded_data_store = urllib.parse.quote(data_store, safe='')
    encoded_entry = urllib.parse.quote(str(user_id), safe='')

    url = f"{base_url}universes/{universe}/data-stores/{encoded_data_store}/scopes/{scope}/entries/{encoded_entry}"
    headers = {apiHeaderKey: apiKey}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error fetching entry for user {user_id}: {response.status_code}, {response.text}")
        return None

    return response.json()


def update_entry(universe, data_store, user_id, new_value, scope='global'):
    encoded_data_store = urllib.parse.quote(data_store, safe='')
    encoded_entry = urllib.parse.quote(str(user_id), safe='')

    url = f"{base_url}universes/{universe}/data-stores/{encoded_data_store}/scopes/{scope}/entries/{encoded_entry}"
    headers = {
        apiHeaderKey: apiKey,
        'Content-Type': 'application/json'
    }

    payload = json.dumps({'value': new_value})
    response = requests.patch(url, headers=headers, data=payload)

    if response.status_code != 200:
        print(f"Error updating entry for user {user_id}: {response.status_code}, {response.text}")
    else:
        print(f"Successfully updated entry for user {user_id}")

    return response


user_id = 61574406

entry = get_entry_by_userid(universe_id, data_store_name, user_id)

if entry:
    print(f"Current entry for user {user_id}: {entry['value']}")