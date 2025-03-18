import discord
import os

# Token'ı güvenli bir şekilde almak için os modülünü kullanıyoruz
TOKEN = os.getenv("DISCORD_TOKEN")

# Client'ı oluşturuyoruz
client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} olarak giriş yapıldı!')

# Botu çalıştırmak için token kullanıyoruz.
client.run(TOKEN)
