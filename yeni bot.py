from telethon import TelegramClient, events
import asyncio
import os
import json

# AYARLAR
API_ID = int(os.environ.get('API_ID', 27125394))
API_HASH = os.environ.get('API_HASH', 'f83dd11c7c68d4f85951883dd42ffcc5')
SESSION_STRING = os.environ.get('SESSION_STRING', '')  # GitHub Actions için session string kullanacağız
TARGET_CHANNELS = ['firsatlartr', 'FIRSATLAR']  # Kullanıcı adları veya ID'ler
KEYWORDS = ["telefon", "pantolon", "cif", "havlu", "termos", "mont"]

# Son işlenen mesajları takip etmek için
PROCESSED_FILE = "processed_messages.json"

# Telethon istemcisini başlat
client = None

async def init_client():
    global client
    # String session ile başlat (GitHub Actions'da kullanmak için)
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()
    return client

def load_processed_messages():
    if os.path.exists(PROCESSED_FILE):
        try:
            with open(PROCESSED_FILE, 'r') as f:
                return json.load(f)
        except:
            return {'message_ids': []}
    return {'message_ids': []}

def save_processed_messages(data):
    with open(PROCESSED_FILE, 'w') as f:
        json.dump(data, f)

@events.register(events.NewMessage(chats=TARGET_CHANNELS))
async def handle_new_message(event):
    try:
        # Daha önce işlenmiş mesajları kontrol et
        processed_data = load_processed_messages()
        if event.message.id in processed_data['message_ids']:
            print(f"Mesaj zaten işlenmiş: {event.message.id}")
            return
            
        message_text = event.message.text.lower() if event.message.text else ""
        if any(keyword in message_text for keyword in KEYWORDS):
            # Kaynak kanal bilgisini al
            channel = await event.get_chat()
            await client.send_message(
                "me",  # Kayıtlı mesajlara gönder
                f"🚨 **{channel.title}**\n\n{event.message.text}"
            )
            print(f"✅ {channel.title} - Filtrelenmiş mesaj gönderildi")
            
            # İşlenmiş mesajları kaydet
            processed_data['message_ids'].append(event.message.id)
            # Listeyi son 100 mesajla sınırla
            processed_data['message_ids'] = processed_data['message_ids'][-100:]
            save_processed_messages(processed_data)
            
    except Exception as e:
        print(f"Hata: {e}")

async def main():
    # Telethon StringSession içe aktarımı
    global StringSession
    from telethon.sessions import StringSession
    
    # İstemciyi başlat
    global client
    client = await init_client()
    
    # Kanalları doğrula
    for channel in TARGET_CHANNELS:
        try:
            entity = await client.get_entity(channel)
            print(f"✅ Kanal bağlandı: {entity.title}")
        except Exception as e:
            print(f"❌ HATA: {channel} bulunamadı! ({e})")

    # Event handler'ı ekle
    client.add_event_handler(handle_new_message)
    
    print("Bot çalışıyor... Mesajlar dinleniyor.")
    
    # GitHub Actions için - belirli bir süre çalıştır ve kapat
    # (Normalde await client.run_until_disconnected() kullanılır)
    await asyncio.sleep(600)  # 10 dakika çalış
    await client.disconnect()
    print("Bot planlı şekilde durduruldu.")

if __name__ == '__main__':
    asyncio.run(main())
