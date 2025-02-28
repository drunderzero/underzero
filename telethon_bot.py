from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio
import os
import json

# Debug: Tüm ortam değişkenlerini yazdır
print("Environment Variables:", os.environ)

# AYARLAR
API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
SESSION_STRING = os.environ['SESSION_STRING']

# Debug kontrolü
print(f"API_ID: {API_ID} ({type(API_ID)})")
print(f"API_HASH: {API_HASH} ({type(API_HASH)})")
print(f"SESSION_STRING: {SESSION_STRING[:15]}...")  # Güvenlik nedeniyle tam string loglanmıyor

TARGET_CHANNELS = ['firsatlartr', 'FIRSATLAR']
KEYWORDS = ["telefon", "pantolon", "cif", "havlu", "termos", "mont"]
PROCESSED_FILE = "processed_messages.json"

def load_processed_messages():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, 'r') as f:
            return json.load(f)
    return {'message_ids': []}

def save_processed_messages(data):
    with open(PROCESSED_FILE, 'w') as f:
        json.dump(data, f)

async def init_client():
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()
    return client

@events.register(events.NewMessage(chats=TARGET_CHANNELS))
async def handle_new_message(event):
    try:
        processed_data = load_processed_messages()
        if event.message.id in processed_data.get('message_ids', []):
            return
        # Mesajın text içeriği yoksa devam etme
        if not event.message.text:
            return
        message_text = event.message.text.lower()
        if any(keyword in message_text for keyword in KEYWORDS):
            channel = await event.get_chat()
            await event.client.send_message(
                "me",
                f"🚨 **{channel.title}**\n\n{event.message.text}"
            )
            processed_data['message_ids'].append(event.message.id)
            # Son 100 mesaj ID'sini sakla
            processed_data['message_ids'] = processed_data['message_ids'][-100:]
            save_processed_messages(processed_data)
    except Exception as e:
        print(f"Hata: {e}")

async def main():
    client = await init_client()
    
    # Hedef kanallara bağlanmayı kontrol et
    for channel in TARGET_CHANNELS:
        try:
            entity = await client.get_entity(channel)
            print(f"✅ Kanal bağlandı: {entity.title}")
        except ValueError:
            print(f"❌ Kanal bulunamadı: {channel}")
            await client.disconnect()
            return

    # Olay işleyiciyi ekle
    client.add_event_handler(handle_new_message)
    print("Bot çalışıyor...")
    
    # GitHub Actions için 1 saatlik bekleme süresi
    await asyncio.sleep(3600)
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
