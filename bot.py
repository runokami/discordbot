import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io
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

def create_rank_image(user, rank, xp):
    # Arka plan resmi oluşturma veya yükleme
    image = Image.new("RGB", (600, 200), color=(54, 57, 63))  # Discord'un koyu temasına uygun renk

    draw = ImageDraw.Draw(image)

    # Yazı tipi ve boyutunu ayarlama
    font = ImageFont.truetype("arial.ttf", 30)  # Arial yazı tipini kullanıyoruz, isterseniz başka bir yazı tipi kullanabilirsiniz

    # Kullanıcı adını ekleme
    draw.text((20, 20), f"Kullanıcı: {user.name}", font=font, fill=(255, 255, 255))

    # Sıralamayı ekleme
    draw.text((20, 80), f"Sıralama: {rank}", font=font, fill=(255, 255, 255))

    # XP'yi ekleme
    draw.text((20, 140), f"XP: {xp}", font=font, fill=(255, 255, 255))

    # Resmi bellekte saklama
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes.seek(0)

    return image_bytes

@bot.command()
async def rank(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author

    guild_id = str(ctx.guild.id)

    with open("xp.json", "r") as f:
        data = json.load(f)

    if guild_id not in data:
        await ctx.send("Bu sunucuda henüz XP verisi yok.")
        return

    users = data[guild_id]

    if str(user.id) not in users:
        await ctx.send("Bu kullanıcının henüz XP'si yok.")
        return

    user_xp = users[str(user.id)]

    sorted_users = sorted(users.items(), key=lambda x: x[1], reverse=True)

    rank = 0
    for i, (user_id, xp) in enumerate(sorted_users):
        if str(user.id) == str(user.id):
            rank = i + 1
            break

    # Görseli oluşturma
    image_bytes = create_rank_image(user, rank, user_xp)

    # Görseli gönderme
    await ctx.send(file=discord.File(image_bytes, "rank.png"))

# XP ekleme fonksiyonu
def add_xp(guild_id, user_id, xp):
    with open("xp.json", "r") as f:
        data = json.load(f)

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

    # guild_id, mesajın gönderildiği sunucunun ID'sidir
    guild_id = message.guild.id

    # user_id, mesajı gönderen kullanıcının ID'sidir
    user_id = message.author.id

    xp = distribute_random_xp(guild_id, user_id)
    print(f"{message.guild.name} sunucusunda {message.author.name} kullanıcısına {xp} XP eklendi.")

    await bot.process_commands(message) # Komutları işle

# Bot hazır olduğunda çalışacak kod
@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yaptık!")

# Botu çalıştır
bot.run(TOKEN)
