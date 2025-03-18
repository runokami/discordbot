import discord
from discord.ext import commands
import os
import json

# Botun token'ı
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents nesnesini oluşturuyoruz
intents = discord.Intents.all()

# Botu oluşturuyoruz
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)  # help_command=None ile varsayılan help komutunu devre dışı bırakıyoruz

# Embed'leri saklamak için JSON dosyasının yolu
EMBEDS_FILE = 'embeds/embeds.json'

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

# Embed listeleme komutu
@bot.command()
async def embed_list(ctx):
    embeds = load_embeds()
    
    if not embeds:
        await ctx.send("Şu anda herhangi bir embed bulunmuyor.")
        return
    
    embed_names = "\n".join([f"- {embed}" for embed in embeds.keys()])
    await ctx.send(f"Mevcut embed'ler:\n{embed_names}")

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

# Embed başlık ayarlama komutu
@bot.command()
@commands.has_permissions(manage_messages=True)
async def embed_title(ctx, embed_name, title):
    embeds = load_embeds()
    
    if embed_name not in embeds:
        await ctx.send(f"'{embed_name}' adlı embed bulunamadı.")
        return

    # Başlık değiştirilmiş oluyor
    embeds[embed_name]["title"] = title
    save_embeds(embeds)  # Değişiklikleri kaydediyoruz
    
    # Embed'in önizlemesini gönderiyoruz
    embed = discord.Embed(
        title=embeds[embed_name]["title"],
        description=embeds[embed_name]["description"],
        color=discord.Color(int(embeds[embed_name]["color"].lstrip('#'), 16))
    )
    await ctx.send(f"'{embed_name}' adlı embed'in başlığı '{title}' olarak değiştirildi.", embed=embed)

# Embed açıklama ayarlama komutu
@bot.command()
@commands.has_permissions(manage_messages=True)
async def embed_description(ctx, embed_name, description):
    embeds = load_embeds()
    
    if embed_name not in embeds:
        await ctx.send(f"'{embed_name}' adlı embed bulunamadı.")
        return

    # Açıklama değiştirilmiş oluyor
    embeds[embed_name]["description"] = description
    save_embeds(embeds)  # Değişiklikleri kaydediyoruz
    
    # Embed'in önizlemesini gönderiyoruz
    embed = discord.Embed(
        title=embeds[embed_name]["title"],
        description=embeds[embed_name]["description"],
        color=discord.Color(int(embeds[embed_name]["color"].lstrip('#'), 16))
    )
    await ctx.send(f"'{embed_name}' adlı embed'in açıklaması '{description}' olarak değiştirildi.", embed=embed)

# Embed rengini değiştirme komutu (Hex formatında)
@bot.command()
@commands.has_permissions(manage_messages=True)
async def embed_color(ctx, embed_name, color_hex):
    embeds = load_embeds()

    if embed_name not in embeds:
        await ctx.send(f"'{embed_name}' adlı embed bulunamadı.")
        return

    try:
        # Hex rengini doğru bir şekilde parse etme
        color = discord.Color(int(color_hex.lstrip('#'), 16))  # Hex rengini alıyoruz
        embeds[embed_name]["color"] = color_hex  # Rengi kaydediyoruz
        save_embeds(embeds)  # Değişiklikleri kaydediyoruz
        
        # Embed'in önizlemesini gönderiyoruz
        embed = discord.Embed(
            title=embeds[embed_name]["title"],
            description=embeds[embed_name]["description"],
            color=color
        )
        await ctx.send(f"'{embed_name}' adlı embed'in rengi '{color_hex}' olarak değiştirildi.", embed=embed)
    except ValueError:
        await ctx.send("Geçersiz renk kodu! Lütfen geçerli bir hex renk kodu girin (örneğin #ffffff).")

# Embed mesajını gönderme komutu
@bot.command()
async def embed_send(ctx, embed_name):
    embeds = load_embeds()
    
    if embed_name not in embeds:
        await ctx.send(f"'{embed_name}' adlı embed bulunamadı.")
        return

    embed_data = embeds[embed_name]
    
    # Rengi hex formatından alıp discord.Color ile kullanıyoruz
    try:
        color = discord.Color(int(embed_data["color"].lstrip('#'), 16))
    except ValueError:
        color = discord.Color.blue()  # Eğer renk hatalıysa varsayılan mavi olarak ayarla

    embed = discord.Embed(
        title=embed_data["title"],
        description=embed_data["description"],
        color=color
    )
    
    # Embed mesajını gönderiyoruz
    await ctx.send(embed=embed)

# !help komutu ile bot komutları hakkında bilgi verme
@bot.command()
async def help(ctx):
    help_message = """
    **Bot Komutları:**
    
    **!embed create <embed_ismi>** - Yeni bir embed oluşturur.
    **!embed title <embed_ismi> <title>** - Embed başlığını değiştirir.
    **!embed description <embed_ismi> <description>** - Embed açıklamasını değiştirir.
    **!embed color <embed_ismi> <hex_color>** - Embed rengini değiştirir (hex renk kodu ile).
    **!embed send <embed_ismi>** - Embed mesajını gönderir.
    **!embed list** - Mevcut embed'leri listeler.
    
    **Not:** Yalnızca "Mesajları yönetme" yetkisine sahip kullanıcılar embed'leri oluşturabilir ve düzenleyebilir.
    """
    await ctx.send(help_message)

# Botu başlatıyoruz
bot.run(TOKEN)
