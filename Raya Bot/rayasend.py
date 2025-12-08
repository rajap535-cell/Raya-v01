import requests

# Your actual credentials go here
access_token = 'EAASAvYrwZAQsBPD6YJZB4p7wCGiw1iovQ9OhIfZB3WLJX2P0D5CEilZBxPAzGxOS1oXdiaZB6ZAUh5MzZCs2skIFFEDJ4bIqEhq5SIQZCF4bqoQxrQLkMNoLhZBZAOQG09ZB4JvKJJzA2yXIDEhLf0ChjGMHCkPxMUNgUsU9e8JKZBH32ZB5rx5QZB2nmZAflZA42uQqQyFmgLGHZBAyUAUld8Sk8NNfxpiZBfNgsKoTT4VLg7YhZAx'
phone_number_id = '738910609304201'
recipient_phone = '+916295372604'  # Use full country code and number
message_text = 'Hello from RAYA! WhatsApp Cloud API works!'

url = f'https://graph.facebook.com/v19.0/{phone_number_id}/messages'

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

payload = {
  "messaging_product": "whatsapp",
  "to": "917319030476",
  "type": "template",
  "template": {
    "name": "hello_world",
    "language": {
      "code": "en_us"
    }
  }
}

response = requests.post(url, headers=headers, json=payload)

print('Status:', response.status_code)
print('Response:', response.json())
