from telethon import TelegramClient, events
from telethon.sessions import StringSession  # StringSession'ı en üste taşı
import asyncio
import os
import json

# Debug: Tüm ortam değişkenlerini yazdır
print("Environment Variables:", os.environ)

# AYARLAR (TEK BİR TANIMLAMA YAPIN)
API_ID = int(os.environ['API_ID'])  # Secrets'da MECBURİ olmalı
API_HASH = os.environ['API_HASH']
SESSION_STRING = os.environ['SESSION_STRING']

# Debug kontrolü
print(f"API_ID: {API_ID} ({type(API_ID)})")
print(f"API_HASH: {API_HASH} ({type(API_HASH)})")
print(f"SESSION_STRING: {SESSION_STRING[:15]}...")  # Full string'i loglama güvenlik riski!

TARGET_CHANNELS = ['firsatlartr', 'FIRSATLAR']
KEYWORDS = ["telefon", "pantolon", "cif", "havlu", "termos", "mont"]
PROCESSED_FILE = "processed_messages.json"

# 1. YANLIŞ: API_ID'yi iki kez tanımlamışsınız
# 2. YANLIŞ: Default değerler kullanıyorsunuz (GitHub Secrets MECBURİ)
# 3. YANLIŞ: StringSession geç import edilmiş

async def init_client():
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()
    return client

# ... (load_processed_messages ve save_processed_messages aynı kalabilir)

@events.register(events.NewMessage(chats=TARGET_CHANNELS))
async def handle_new_message(event):
    try:
        processed_data = load_processed_messages()
        if event.message.id in processed_data['message_ids']:
            return
            
        message_text = event.message.text.lower()
        if any(keyword in message_text for keyword in KEYWORDS):
            channel = await event.get_chat()
            await client.send_message(
                "me",
                f"🚨 **{channel.title}**\n\n{event.message.text}"
            )
            processed_data['message_ids'].append(event.message.id)
            processed_data['message_ids'] = processed_data['message_ids'][-100:]
            save_processed_messages(processed_data)
            
    except Exception as e:
        print(f"Hata: {e}")

async def main():
    client = await init_client()
    
    # Kanalları kontrol et
    for channel in TARGET_CHANNELS:
        try:
            entity = await client.get_entity(channel)
            print(f"✅ Kanal bağlandı: {entity.title}")
        except ValueError:
            print(f"❌ Kanal bulunamadı: {channel}")
            await client.disconnect()
            return  # Kritik hata durumunda çık

    client.add_event_handler(handle_new_message)
    print("Bot çalışıyor...")
    
    # GitHub Actions için timeout süresini 1 saat yap
    await asyncio.sleep(3600)
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
