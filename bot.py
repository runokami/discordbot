import discord
from discord.ext import commands
import json
import os
import random

TOKEN = os.getenv("DISCORD_TOKEN")  
EMBED_FILE = "embeds.json"  # Embedlerin kaydedildiği dosya
XP_FILE = "xp.json"  # XP sisteminin kaydedildiği dosya

# 📂 JSON Dosya Yönetimi
def load_json(filename):
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({}, f)  # Eğer dosya yoksa boş bir JSON oluştur
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# 📥 EMBED SİSTEMİ
def get_guild_embeds(guild_id):
    embeds = load_json(EMBED_FILE)
    if str(guild_id) not in embeds:
        embeds[str(guild_id)] = {}
        save_json(EMBED_FILE, embeds)
    return embeds[str(guild_id)]

def save_guild_embeds(guild_id, data):
    embeds = load_json(EMBED_FILE)
    embeds[str(guild_id)] = data
    save_json(EMBED_FILE, embeds)

# 📥 XP SİSTEMİ
def get_guild_xp(guild_id):
    xp_data = load_json(XP_FILE)
    if str(guild_id) not in xp_data:
        xp_data[str(guild_id)] = {}
        save_json(XP_FILE, xp_data)
    return xp_data[str(guild_id)]

def save_guild_xp(guild_id, data):
    xp_data = load_json(XP_FILE)
    xp_data[str(guild_id)] = data
    save_json(XP_FILE, xp_data)

# 🤖 Botu oluştur
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)  # help_command=None ile varsayılan yardımı devre dışı bırakıyoruz

@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yapıldı!")

# 📌 **!help → Özel Yardım Komutu**
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="📜 Komut Listesi", color=0x3498db)
    embed.add_field(name="!ping", value="Pong! Botun çalışıp çalışmadığını kontrol eder.", inline=False)
    embed.add_field(name="!embed create <isim>", value="Yeni bir embed oluşturur.", inline=False)
    embed.add_field(name="!embed title <isim> <başlık>", value="Embed başlığını ayarlar.", inline=False)
    embed.add_field(name="!embed description <isim> <açıklama>", value="Embed açıklamasını ayarlar.", inline=False)
    embed.add_field(name="!embed color <isim> <#hex>", value="Embed rengini ayarlar.", inline=False)
    embed.add_field(name="!embed image <isim> <URL>", value="Embed görselini ayarlar.", inline=False)
    embed.add_field(name="!embed send <isim>", value="Embed'i kanala gönderir.", inline=False)
    embed.add_field(name="!embed list", value="Sunucudaki tüm embedleri listeler.", inline=False)
    embed.add_field(name="!rank", value="XP sisteminden seviyenizi gösterir.", inline=False)
    await ctx.send(embed=embed)

# 📌 **!embed list → Sunucudaki Tüm Embedleri Listeleme**
@bot.command()
async def embed_list(ctx):
    guild_id = ctx.guild.id
    embeds = get_guild_embeds(guild_id)

    if not embeds:
        await ctx.send("📭 **Bu sunucu için hiç embed oluşturulmamış!**")
        return

    embed = discord.Embed(title="📜 Embed Listesi", color=0x00FF00)
    for embed_name in embeds.keys():
        embed.add_field(name=embed_name, value="Ayarlandı ✅", inline=False)

    await ctx.send(embed=embed)

# 📌 **XP SİSTEMİ (Seviye ve Rank)**
@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Bot mesajlarını yok say

    guild_id = message.guild.id
    user_id = str(message.author.id)
    xp_data = get_guild_xp(guild_id)

    if user_id not in xp_data:
        xp_data[user_id] = {"xp": 0, "level": 1}

    xp_data[user_id]["xp"] += random.randint(5, 15)  # 5-15 XP rastgele ekle
    current_xp = xp_data[user_id]["xp"]
    level = xp_data[user_id]["level"]

    # 🆙 Seviye Atlatma Sistemi
    if current_xp >= level * 100:  # Örneğin, 1. seviyeden 2. seviyeye 100 XP gerekir.
        xp_data[user_id]["xp"] = 0
        xp_data[user_id]["level"] += 1
        await message.channel.send(f"🎉 {message.author.mention} **{level+1}. seviyeye ulaştı!**")

    save_guild_xp(guild_id, xp_data)

    await bot.process_commands(message)

# 📌 **!rank → Kullanıcının XP ve Seviyesini Göster**
@bot.command()
async def rank(ctx, member: discord.Member = None):
    member = member or ctx.author  # Eğer kullanıcı birisini etiketlemezse kendisini alır
    guild_id = ctx.guild.id
    user_id = str(member.id)
    xp_data = get_guild_xp(guild_id)

    if user_id not in xp_data:
        await ctx.send(f"❌ {member.mention} için herhangi bir XP verisi bulunamadı!")
        return

    xp = xp_data[user_id]["xp"]
    level = xp_data[user_id]["level"]

    embed = discord.Embed(title=f"{member.name} - Rank", color=0xFFD700)
    embed.add_field(name="Seviye", value=level, inline=True)
    embed.add_field(name="XP", value=f"{xp}/{level*100}", inline=True)

    await ctx.send(embed=embed)

# 🚀 **Botu Başlat**
bot.run(TOKEN)
