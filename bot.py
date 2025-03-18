import discord
import os

# Token'ı güvenli bir şekilde almak için os modülünü kullanıyoruz
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents nesnesini oluşturuyoruz
intents = discord.Intents.default()  # Varsayılan intents
intents.message_content = True  # Mesaj içeriğini alabilmek için gerekli izin

# Client'ı oluşturuyoruz ve intents'i geçiriyoruz
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} olarak giriş yapıldı!')

# Botu çalıştırmak için token kullanıyoruz
client.run(TOKEN)
