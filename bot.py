import discord
from discord.ext import commands
import os
import json

# Botun token'ı
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents nesnesini oluşturuyoruz
intents = discord.Intents.all()

# Botu oluşturuyoruz
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Ping komutunu tanımlıyoruz
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Embed gönderme komutunu tanımlıyoruz
@bot.command()
async def embed(ctx):
    embed = discord.Embed(
        title="Başlık Buraya",
        description="Açıklama Buraya",
        color=discord.Color.blue()  # Embed rengini mavi yapıyoruz
    )
    await ctx.send(embed=embed)

# Embed'leri saklamak için JSON dosyasının yolu
EMBEDS_FILE = 'embeds.json'

# Embed'leri dosyadan yüklemek için fonksiyon
def load_embeds():
    if not os.path.exists(EMBEDS_FILE):
        return {}
    with open(EMBEDS_FILE, 'r') as file:
        return json.load(file)

# Embed'leri dosyaya kaydetmek için fonksiyon
def save_embeds(embeds):
    with open(EMBEDS_FILE, 'w') as file:
        json.dump(embeds, file, indent=4)

# Embed oluşturma komutu
@bot.command()
@commands.has_permissions(manage_messages=True)
async def embed_create(ctx, embed_name):
    embeds = load_embeds()
    
    if embed_name in embeds:
        await ctx.send(f"'{embed_name}' adlı bir embed zaten mevcut.")
        return

    # Yeni embed nesnesi oluşturuluyor
    embeds[embed_name] = {
        "title": "Başlık Buraya", 
        "description": "Açıklama Buraya", 
        "color": "#0000FF"  # Varsayılan renk mavi (hex formatında)
    }

    # Embed'leri kaydediyoruz
    save_embeds(embeds)
    
    # Embed'in önizlemesini gönderiyoruz
    embed = discord.Embed(
        title=embeds[embed_name]["title"],
        description=embeds[embed_name]["description"],
        color=discord.Color(int(embeds[embed_name]["color"].lstrip('#'), 16))
    )
    await ctx.send(f"'{embed_name}' adlı embed başarıyla oluşturuldu.", embed=embed)

# Botu başlatıyoruz
bot.run(TOKEN)
