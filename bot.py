import discord
from discord.ext import commands
import random
import json
import os

# Ortam değişkeninden bot token'ını al
TOKEN = os.environ.get("DISCORD_TOKEN")

# Tüm intent'leri etkinleştir
intents = discord.Intents.all()

# Bot nesnesini oluştur
bot = commands.Bot(command_prefix="!", intents=intents)

# Veri dosyasını oluştur (gerekirse)
if not os.path.exists("xp.json"):
    with open("xp.json", "w") as f:
        json.dump({}, f)

    guild_id = str(guild_id)
    user_id = str(user_id)

    if guild_id not in data:
        data[guild_id] = {}

    if user_id not in data[guild_id]:
        data[guild_id][user_id] = 0

    data[guild_id][user_id] += xp

    with open("xp.json", "w") as f:
        json.dump(data, f)

# Rastgele XP dağıtımı fonksiyonu
def distribute_random_xp(guild_id, user_id):
    chance = random.random()

    if chance < 0.60:
        xp = 0
    elif chance < 0.75:
        xp = 5
    elif chance < 0.85:
        xp = 10
    elif chance < 0.90:
        xp = 15
    elif chance < 0.925:
        xp = 20
    else:
        xp = 25

    add_xp(guild_id, user_id, xp)
    return xp

# Mesaj olayını işle
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    xp = distribute_random_xp(message.guild.id, message.author.id)
    print(f"{message.guild.name} sunucusunda {message.author.name} kullanıcısına {xp} XP eklendi.")

    await bot.process_commands(message) # Komutları işle


# Bot hazır olduğunda çalışacak kod
@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yaptık!")
    await tree.sync()

# Botu çalıştır
bot.run(TOKEN)
