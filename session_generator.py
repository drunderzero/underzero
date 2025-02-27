from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Bu scripti LOCAL bilgisayarınızda bir kez çalıştırarak session string elde edin
# Bu string'i GitHub secrets olarak kaydedin

API_ID = 27125394  # API ID'nizi girin
API_HASH = 'f83dd11c7c68d4f85951883dd42ffcc5'  # API Hash'inizi girin

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    print("Lütfen Telegram hesabınıza giriş yapın.")
    client.send_message("me", "Merhaba! Bu mesaj session'ın başarıyla oluşturulduğunu gösterir.")
    print("Aşağıdaki session string'i kopyalayıp GitHub Secrets'a 'SESSION_STRING' olarak ekleyin:")
    print(client.session.save())