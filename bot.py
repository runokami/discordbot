import discord
from discord.ext import commands
from discord import app_commands
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import requests
from io import BytesIO
import os
import random

TOKEN = os.environ.get("DISCORD_TOKEN")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

def load_embed_data():
    try:
        with open("embed_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_embed_data(data):
    with open("embed_data.json", "w") as f:
        json.dump(data, f)

def get_embeds(guild_id):
    data = load_embed_data()
    guild_id = str(guild_id)
    if guild_id not in data:
        data[guild_id] = {}
    return data[guild_id]

def set_embeds(guild_id, embeds):
    data = load_embed_data()
    guild_id = str(guild_id)
    data[guild_id] = embeds
    save_embed_data(data)

def create_embed(title, description, color=discord.Color.blue()):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    return embed

@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yaptık!")
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} adet komut senkronize edildi.")
    except Exception as e:
        print(e)

@bot.tree.command(name="embed", description="Embed mesajı gönderir.")
async def embed_slash(interaction: discord.Interaction, title: str, description: str, color: str = None):
    if color:
        try:
            color = discord.Color.from_str(color)
        except ValueError:
            color = discord.Color.blue()
    else:
        color = discord.Color.blue()

    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    await interaction.response.send_message(embed=embed)

@bot.command()
async def embed(ctx):
    await ctx.send("Başlık?")
    title = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)

    await ctx.send("Açıklama?")
    description = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)

    await ctx.send("Renk (isteğe bağlı, örn. #RRGGBB veya blue):")
    color_message = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
    color = color_message.content

    try:
        color = discord.Color.from_str(color) # Düzeltilen satır
    except ValueError:
        color = discord.Color.blue()

    embed = discord.Embed(
        title=title.content,
        description=description.content,
        color=color
    )
    embeds = get_embeds(ctx.guild.id)
    embed_id = len(embeds) + 1
    embeds[embed_id] = embed.to_dict()
    set_embeds(ctx.guild.id, embeds)

    await ctx.send(embed=embed)

@bot.tree.command(name="embed_show", description="Belirli bir embed'i gösterir.")
async def embed_show_slash(interaction: discord.Interaction, embed_id: int):
    embeds = get_embeds(interaction.guild.id)
    if embed_id not in embeds:
        await interaction.response.send_message("Bu ID'ye sahip bir embed bulunamadı.")
        return

    embed_data = embeds[embed_id]
    embed = discord.Embed.from_dict(embed_data)
    await interaction.response.send_message(embed=embed)

@embed_show_slash.autocomplete('embed_id')
async def embed_id_autocomplete(interaction: discord.Interaction, current: str):
    embeds = get_embeds(interaction.guild.id)
    return [
        app_commands.Choice(name=f"{embed_id}: {embed_data['title']}", value=embed_id)
        for embed_id, embed_data in embeds.items()
        if current.lower() in str(embed_id).lower() or current.lower() in embed_data['title'].lower()
    ]

@bot.tree.command(name="embed_list", description="Sunucudaki embed'lerin listesini gösterir.")
async def embed_list_slash(interaction: discord.Interaction):
    embeds = get_embeds(interaction.guild.id)
    if not embeds:
        await interaction.response.send_message("Bu sunucuda kayıtlı embed bulunmuyor.")
        return

    embed_list = "\n".join(f"{embed_id}: {embed_data['title']}" for embed_id, embed_data in embeds.items())
    await interaction.response.send_message(f"Kayıtlı Embedler:\n{embed_list}")

def seviye_karti_olustur(avatar_url, kullanici_adi, seviye, mevcut_xp, gerekli_xp, rutbe, durum, bar_rengi="#3498db"):
    """
    Dinamik seviye kartı oluşturur.

    Args:
        avatar_url (str): Kullanıcının avatar URL'si.
        kullanici_adi (str): Kullanıcının adı.
        seviye (int): Kullanıcının seviyesi.
        mevcut_xp (int): Kullanıcının mevcut XP'si.
        gerekli_xp (int): Bir sonraki seviye için gereken XP.
        rutbe (str): Kullanıcının rütbesi.
        durum (str): Kullanıcının Discord durumu ("online", "idle", "dnd", "offline").
        bar_rengi (str, optional): Progress bar rengi (hex kodu). Varsayılan: #3498db.

    Returns:
        BytesIO: Oluşturulan seviye kartının resim verisi.
    """

    # Ana dikdörtgen
    genislik, yukseklik = 930, 275
    ana_dikdortgen = Image.new("RGB", (genislik, yukseklik), "gray")
    cizim = ImageDraw.Draw(ana_dikdortgen)

    # İç dikdörtgen
    ic_dikdortgen = Image.new("RGB", (900, 250), "black")
    ana_dikdortgen.paste(ic_dikdortgen, (15, 12))

    # Avatar
    try:
        avatar_resmi = Image.open(BytesIO(requests.get(avatar_url).content)).resize((200, 200))
    except Exception as e:
        print(f"Avatar yüklenirken hata oluştu: {e}")
        return None  # Hata durumunda None döndür

    # Yuvarlak avatar maskesi
    maske = Image.new("L", (200, 200), 0)
    cizim_maske = ImageDraw.Draw(maske)
    cizim_maske.ellipse((0, 0, 200, 200), fill=255)
    ana_dikdortgen.paste(avatar_resmi, (50, 37), maske)

    # Durum göstergesi (yuvarlak)
    durum_renkleri = {
        "online": "green",
        "idle": "yellow",
        "dnd": "red",
        "offline": "gray",
    }
    durum_renk = durum_renkleri.get(durum, "gray")  # Geçersiz durum için varsayılan olarak gri

    cizim.ellipse((220, 25, 240, 45), fill=durum_renk)

    # Avatar çerçevesi (siyah)
    cizim.rounded_rectangle((48, 35, 252, 239), radius=10, outline="black", width=2)

    # Progress bar
    progress_genislik = 700
    progress_baslangic_x = 450
    progress_bitis_x = progress_baslangic_x + progress_genislik
    progress_yukseklik = 20
    progress_y = 150
    progress_doluluk = int((mevcut_xp / gerekli_xp) * progress_genislik)

    cizim.rounded_rectangle((progress_baslangic_x, progress_y, progress_bitis_x, progress_y + progress_yukseklik), radius=10, outline="white", width=2)
    cizim.rounded_rectangle((progress_baslangic_x, progress_y, progress_baslangic_x + progress_doluluk, progress_y + progress_yukseklik), radius=10, fill=bar_rengi)

    # Metinler
    font_kullanici_adi = ImageFont.truetype("arial.ttf", 30)  # İstediğiniz fontu kullanabilirsiniz
    font_xp = ImageFont.truetype("arial.ttf", 20)
    font_rutbe_seviye = ImageFont.truetype("arial.ttf", 25)

    cizim.text((progress_baslangic_x, progress_y - 35), kullanici_adi, font=font_kullanici_adi, fill="white")
    cizim.text((progress_bitis_x - 150, progress_y + 30), f"{mevcut_xp} / {gerekli_xp} XP", font=font_xp, fill="white")
    cizim.text((500, 100), f"{rutbe} | Seviye {seviye}", font=font_rutbe_seviye, fill="white")

    # Resim verisini BytesIO nesnesine kaydet
    resim_verisi = BytesIO()
    ana_dikdortgen.save(resim_verisi, format="PNG")
    resim_verisi.seek(0)

    return resim_verisi

# Kullanım örneği
avatar_url = "Kullanıcı Avatar URL'si"
kullanici_adi = "Kullanıcı Adı"
seviye = 5
mevcut_xp = 750
gerekli_xp = 1000
rutbe = "#10"
durum = "online"
bar_rengi = "#ff0000"  # Kırmızı renk

resim_verisi = seviye_karti_olustur(avatar_url, kullanici_adi, seviye, mevcut_xp, gerekli_xp, rutbe, durum, bar_rengi)

if resim_verisi:
    # resim_verisi'ni Discord'a gönderebilir veya kaydedebilirsiniz
    with open("seviye_karti.png", "wb") as f:
        f.write(resim_verisi.getvalue())

@bot.command(name="rank")
async def rank_komut(ctx, kullanici: discord.Member = None):
    """
    !rank komutu ile seviye kartı oluşturur.
    """
    if kullanici is None:
        kullanici = ctx.author

    avatar_url = kullanici.avatar.url
    kullanici_adi = kullanici.name
    seviye = 5  # Örnek seviye
    mevcut_xp = 750  # Örnek mevcut XP
    gerekli_xp = 1000  # Örnek gerekli XP
    rutbe = "#10"  # Örnek rütbe
    durum = kullanici.status.name  # Kullanıcının Discord durumu
    bar_rengi = "#ff0000"  # Örnek progress bar rengi

    resim_verisi = seviye_karti_olustur(avatar_url, kullanici_adi, seviye, mevcut_xp, gerekli_xp, rutbe, durum, bar_rengi)

    if resim_verisi:
        dosya = discord.File(resim_verisi, filename="seviye_karti.png")
        await ctx.send(file=dosya)
    else:
        await ctx.send("Seviye kartı oluşturulurken bir hata oluştu.")

@bot.tree.command(name="rank", description="Seviye kartı oluşturur.")
async def rank_slash_komut(ctx, kullanici: discord.Member = None):
    """
    /rank komutu ile seviye kartı oluşturur.
    """
    if kullanici is None:
        kullanici = ctx.author

    avatar_url = kullanici.avatar.url
    kullanici_adi = kullanici.name
    seviye = 5  # Örnek seviye
    mevcut_xp = 750  # Örnek mevcut XP
    gerekli_xp = 1000  # Örnek gerekli XP
    rutbe = "#10"  # Örnek rütbe
    durum = kullanici.status.name  # Kullanıcının Discord durumu
    bar_rengi = "#ff0000"  # Örnek progress bar rengi

    resim_verisi = seviye_karti_olustur(avatar_url, kullanici_adi, seviye, mevcut_xp, gerekli_xp, rutbe, durum, bar_rengi)

    if resim_verisi:
        dosya = discord.File(resim_verisi, filename="seviye_karti.png")
        await ctx.respond(file=dosya)
    else:
        await ctx.respond("Seviye kartı oluşturulurken bir hata oluştu.")

bot.run(TOKEN)
