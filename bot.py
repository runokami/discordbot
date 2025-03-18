import discord
from discord.ext import commands
import sqlite3
import os

# Token'ı güvenli bir şekilde almak için os modülünü kullanıyoruz
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents nesnesini oluşturuyoruz
intents = discord.Intents.default()
intents.message_content = True

# Botu oluşturuyoruz
bot = commands.Bot(command_prefix="!", intents=intents)

# Veritabanı bağlantısı
conn = sqlite3.connect('xp_database.db')
cursor = conn.cursor()

# Kullanıcılar için tabloyu oluşturuyoruz
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    xp INTEGER NOT NULL DEFAULT 0
)
''')
conn.commit()

@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yapıldı!')

@bot.command()
async def rank(ctx):
    """Kullanıcının XP bilgisini gösterir"""
    user_id = str(ctx.author.id)
    
    # Kullanıcıyı veritabanından çekiyoruz
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    if user:
        xp = user[2]
        await ctx.send(f'{ctx.author.name} XP: {xp}')
    else:
        await ctx.send(f'{ctx.author.name} XP: 0')

@bot.command()
async def addxp(ctx, xp: int):
    """Kullanıcıya XP ekler"""
    user_id = str(ctx.author.id)
    
    # Kullanıcıyı veritabanından çekiyoruz
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    if user:
        # Kullanıcının XP'sini güncelliyoruz
        new_xp = user[2] + xp
        cursor.execute('UPDATE users SET xp = ? WHERE user_id = ?', (new_xp, user_id))
    else:
        # Yeni kullanıcı ekliyoruz
        cursor.execute('INSERT INTO users (user_id, xp) VALUES (?, ?)', (user_id, xp))
    
    conn.commit()
    await ctx.send(f'{xp} XP {ctx.author.name}\'a eklendi!')

# Botu çalıştırıyoruz
bot.run(TOKEN)
