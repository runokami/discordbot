import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import sqlite3
import random
import os
import re

TOKEN = os.environ.get("DISCORD_TOKEN")
PREFIX = "!"
RANK_CARD_WIDTH = 930
RANK_CARD_HEIGHT = 275

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)
tree = discord.app_commands.CommandTree(bot)

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    xp INTEGER,
    level INTEGER,
    rank TEXT,
    avatar_path TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS embeds (
    ad TEXT PRIMARY KEY,
    baslik TEXT,
    aciklama TEXT,
    renk INTEGER,
    gorsel_url TEXT,
    footer_metni TEXT,
    olusturan TEXT
)
""")

conn.commit()

def load_users():
    cursor.execute("SELECT * FROM users")
    users = {row[0]: {"id": row[0], "xp": row[1], "level": row[2], "rank": row[3], "avatar_path": row[4]} for row in cursor.fetchall()}
    return users

def save_users(users):
    cursor.execute("DELETE FROM users")
    for user in users.values():
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (user["id"], user["xp"], user["level"], user["rank"], user["avatar_path"]))
    conn.commit()

def load_embeds():
    cursor.execute("SELECT * FROM embeds")
    embeds = {row[0]: {"baslik": row[1], "aciklama": row[2], "renk": row[3], "gorsel_url": row[4], "footer_metni": row[5], "olusturan": row[6]} for row in cursor.fetchall()}
    return embeds

def save_embeds(embeds):
    cursor.execute("DELETE FROM embeds")
    for embed in embeds.values():
        cursor.execute("INSERT INTO embeds VALUES (?, ?, ?, ?, ?, ?, ?)", (embed["ad"], embed["baslik"], embed["aciklama"], embed["renk"], embed["gorsel_url"], embed["footer_metni"], embed["olusturan"]))
    conn.commit()

def calculate_level_xp(level):
    return 2 ** level * 100

def generate_rank_card(user):
    avatar = Image.open(user["avatar_path"]).resize((200, 200))

    card = Image.new("RGB", (RANK_CARD_WIDTH, RANK_CARD_HEIGHT), (128, 128, 128))
    inner_card = Image.new("RGB", (RANK_CARD_WIDTH - 5, RANK_CARD_HEIGHT - 5), (0, 0, 0))
    card.paste(inner_card, (3, 3))

    card.paste(avatar, (20, 35))

    draw = ImageDraw.Draw(card)
    font = ImageFont.truetype("arial.ttf", 40)
    small_font = ImageFont.truetype("arial.ttf", 20)

    draw.text((250, 50), f"Seviye: {user['level']}", (255, 255, 255), font=font)
    draw.text((250, 150), f"Rank: {user['rank']}", (255, 255, 255), font=font)

    xp_bar_width = 500
    xp_bar_x = 250
    xp_bar_y = 100

    draw.rectangle((xp_bar_x, xp_bar_y, xp_bar_x + xp_bar_width, xp_bar_y + 20), outline=(255, 255, 255))
    fill_width = int(xp_bar_width * (user["xp"] / calculate_level_xp(user["level"])))
    draw.rectangle((xp_bar_x, xp_bar_y, xp_bar_x + fill_width, xp_bar_y + 20), fill=(0, 255, 0))

    draw.text((xp_bar_x, xp_bar_y + 25), f"{user['xp']} / {calculate_level_xp(user['level'])}", (128, 128, 128), font=small_font)

    card.save(f"rank_{user['id']}.png")
    return f"rank_{user['id']}.png"

def hex_to_int(hex_code):
    hex_code = hex_code.lstrip("#")
    return int(hex_code, 16)

@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yaptık!")
    await tree.sync()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    users = load_users()
    user_id = str(message.author.id)

    if user_id not in users:
        users[user_id] = {
            "id": user_id,
            "xp": 0,
            "level": 0,
            "rank": "Başlangıç",
            "avatar_path": f"avatars/{user_id}.png"
        }
        await message.author.avatar.save(f"avatars/{user_id}.png")

    xp_gained = random.choices([0, 5, 10, 15], weights=[0.5, 0.25, 0.15, 0.1])[0]
    users[user_id]["xp"] += xp_gained

    required_xp = calculate_level_xp(users[user_id]["level"])
    if users[user_id]["xp"] >= required_xp:
        users[user_id]["level"] += 1
        users[user_id]["xp"] -= required_xp
        await message.channel.send(f"{message.author.mention} seviye atladı! Yeni seviye: {users[user_id]['level']}")

    save_users(users)
    await bot.process_commands(message)

@bot.command()
async def rank(ctx):
    user_id = str(ctx.author.id)
    users = load_users()
    if user_id not in users:
        await ctx.send("Henüz bir rank kartınız yok. Mesaj göndererek XP kazanın.")
        return

    rank_card_file = generate_rank_card(users[user_id])
    await ctx.send(file=discord.File(rank_card_file))
    os.remove(rank_card_file)

@bot.command()
async def prefix(ctx, new_prefix):
    global PREFIX
    PREFIX = new_prefix
    bot.command_prefix = new_prefix
    await ctx.send(f"Önek `{new_prefix}` olarak değiştirildi.")

@bot.command()
async def embed_oluştur(ctx, ad: str, başlık: str, açıklama: str, renk: str = "#00FF00", görsel_url: str = None, footer_metni: str = None):
    if not re.match(r'^#([0-9A-Fa-f]{6})$', renk):
        await ctx.send("Geçersiz renk kodu. #ffffff formatında bir hex renk kodu girin.")
        return  # Hata durumunda fonksiyondan çık
    
    color = hex_to_int(renk)
    embeds = load_embeds()
    embeds[ad] = {
        "baslik": baslik,
        "aciklama": aciklama,
        "renk": color,
        "gorsel_url": gorsel_url,
        "footer_metni": footer_metni,
        "olusturan": str(ctx.author.id)
    }
    save_embeds(embeds)
    await ctx.send(f"'{ad}' adında embed oluşturuldu.")
