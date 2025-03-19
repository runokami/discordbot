import discord
from discord.ext import commands
import json
from PIL import Image, ImageDraw, ImageFont
import io
import requests
from io import BytesIO
import os
import random

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

# Kullanıcı avatarını indirme ve yuvarlak hale getirme
def get_user_avatar(user):
    avatar_url = user.avatar.url
    response = requests.get(avatar_url)
    avatar = Image.open(BytesIO(response.content)).resize((100, 100))

    # Yuvarlak maske oluşturma
    mask = Image.new('L', (100, 100), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, 100, 100), fill=255)

    # Avatarı maskeye uygulama
    avatar = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
    avatar.putalpha(mask)

    return avatar

# Kullanıcının aktiflik durumunu alma
def get_user_status_color(user):
    status = user.status
    if status == discord.Status.online:
        return (0, 255, 0)  # Yeşil
    elif status == discord.Status.idle:
        return (255, 255, 0)  # Sarı
    elif status == discord.Status.dnd:
        return (255, 0, 0)  # Kırmızı
    else:
        return (128, 128, 128)  # Gri

# Kullanıcının seviyesini ve XP ilerlemesini hesaplama
def calculate_level(xp):
    level = 0
    required_xp = 100
    while xp >= required_xp:
        level += 1
        xp -= required_xp
        required_xp += 50
    return level, xp, required_xp

# Kullanıcının sıralamasını ve XP'sini alma
def get_user_rank(guild_id, user_id):
    with open("xp.json", "r") as f:
        data = json.load(f)

    if guild_id not in data:
        return None

    users = data[guild_id]

    if str(user_id) not in users:
        return None

    user_xp = users[str(user_id)]

    sorted_users = sorted(users.items(), key=lambda x: x[1], reverse=True)

    rank = 0
    for i, (uid, xp) in enumerate(sorted_users):
        if str(uid) == str(user_id):
            rank = i + 1
            break

    return rank, user_xp

# Görsel oluşturma
def create_rank_image(user, rank, level, current_xp, required_xp):
    # Arka plan resmi oluşturma veya yükleme
    image = Image.new("RGB", (800, 250), color=(54, 57, 63))  # Discord'un koyu temasına uygun renk

    draw = ImageDraw.Draw(image)

    # Yazı tipi ve boyutunu ayarlama (varsayılan yazı tipi)
    font = ImageFont.load_default()

    # Kullanıcı avatarını ekleme
    avatar = get_user_avatar(user)
    image.paste(avatar, (20, 50))

    # Kullanıcı adını ekleme
    draw.text((140, 20), f"{user.name}", font=font, fill=(255, 255, 255))

    # Sıralama ve seviyeyi ekleme
    draw.text((400, 20), f"RÜTBE #{rank} SEVİYE {level}", font=font, fill=(255, 255, 255))

    # XP bilgisini ekleme
    draw.text((600, 20), f"{current_xp} / {required_xp} XP", font=font, fill=(255, 255, 255))

    # İlerleme çubuğu oluşturma
    progress_bar_width = 600
    progress_bar_height = 30
    progress_bar_x = 140
    progress_bar_y = 100

    draw.rectangle((progress_bar_x, progress_bar_y, progress_bar_x + progress_bar_width, progress_bar_y + progress_bar_height), fill=(88, 101, 242))

    # İlerleme miktarını hesaplama
    progress_percentage = current_xp / required_xp
    progress_width = int(progress_bar_width * progress_percentage)

    draw.rectangle((progress_bar_x, progress_bar_y, progress_bar_x + progress_width, progress_bar_y + progress_bar_height), fill=(158, 135, 255))

    # Resmi bellekte saklama
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes.seek(0)

    return image_bytes

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

    guild_id = message.guild.id
    user_id = message.author.id

    xp = distribute_random_xp(guild_id, user_id)
    print(f"{message.guild.name} sunucusunda {message.author.name} kullanıcısına {xp} XP eklendi.")

    await bot.process_commands(message) # Komutları işle

# rank komutu
@bot.command()
async def rank(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author

    guild_id = str(ctx.guild.id)
    user_id = str(user.id)

    rank_data = get_user_rank(guild_id, user_id)

    if rank_data is None:
        await ctx.send("Bu kullanıcı için veri bulunamadı.")
        return

    rank, user_xp = rank_data
    level, current_xp, required_xp = calculate_level(user_xp)

    image_bytes = create_rank_image(user, rank, level, current_xp, required_xp)
    await ctx.send(file=discord.File(image_bytes, "rank.png"))

# Bot hazır olduğunda çalışacak kod
@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yaptık!")

# Botu çalıştır
bot.run(TOKEN)
