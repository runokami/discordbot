import discord
from discord.ext import commands
import os

# Token'ı güvenli bir şekilde almak için os modülünü kullanıyoruz
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents nesnesini oluşturuyoruz
intents = discord.Intents.default()  # Varsayılan intents
intents.message_content = True  # Mesaj içeriğini alabilmek için gerekli izin

# Botu oluşturuyoruz ve prefix olarak "!" belirliyoruz
bot = commands.Bot(command_prefix="!", intents=intents)

# Ping komutunu tanımlıyoruz
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Botun hazır olduğunda mesaj yazdırıyoruz
@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yapıldı!')

# Botu çalıştırmak için token kullanıyoruz
bot.run(TOKEN)
