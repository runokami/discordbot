import discord
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # Token'ı güvenli şekilde alıyoruz

intents = discord.Intents.all()  # Tüm intentsleri açıyoruz
bot = commands.Bot(command_prefix="!", intents=intents)  # Prefix olarak "!" belirliyoruz

@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yapıldı!")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")  # Kullanıcı !ping yazarsa bot Pong! yanıtı verecek

# JSON dosyasını yükleme
def load_embeds():
    if not os.path.exists(EMBED_FILE):
        return {}
    with open(EMBED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# JSON dosyasını kaydetme
def save_embeds(embeds):
    with open(EMBED_FILE, "w", encoding="utf-8") as f:
        json.dump(embeds, f, indent=4, ensure_ascii=False)

# Embed verisini sunucuya özel al
def get_guild_embeds(guild_id):
    embeds = load_embeds()
    if str(guild_id) not in embeds:
        embeds[str(guild_id)] = {"embeds": {}}
        save_embeds(embeds)
    return embeds[str(guild_id)]["embeds"]

# Embed verisini sunucuya özel kaydet
def save_guild_embeds(guild_id, embeds_data):
    embeds = load_embeds()
    embeds[str(guild_id)] = {"embeds": embeds_data}
    save_embeds(embeds)

# Botu oluştur
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yapıldı!")

# Embed oluşturma komutu
@bot.command()
@commands.has_permissions(manage_messages=True)
async def embed_create(ctx, embed_name):
    guild_id = ctx.guild.id
    embeds = get_guild_embeds(guild_id)

    if embed_name in embeds:
        await ctx.send(f"❌ **{embed_name}** adlı embed zaten var!")
        return
    
    embeds[embed_name] = {"title": "", "description": "", "color": "#FFFFFF", "image": ""}
    save_guild_embeds(guild_id, embeds)

    await ctx.send(f"✅ **{embed_name}** adlı embed oluşturuldu!")

# Embed başlık ayarlama komutu
@bot.command()
@commands.has_permissions(manage_messages=True)
async def embed_title(ctx, embed_name, *, title):
    guild_id = ctx.guild.id
    embeds = get_guild_embeds(guild_id)

    if embed_name not in embeds:
        await ctx.send(f"❌ **{embed_name}** adlı embed bulunamadı!")
        return
    
    embeds[embed_name]["title"] = title
    save_guild_embeds(guild_id, embeds)

    await ctx.send(f"✅ **{embed_name}** başlığı **{title}** olarak ayarlandı!")

# Embed açıklama ayarlama komutu
@bot.command()
@commands.has_permissions(manage_messages=True)
async def embed_description(ctx, embed_name, *, description):
    guild_id = ctx.guild.id
    embeds = get_guild_embeds(guild_id)

    if embed_name not in embeds:
        await ctx.send(f"❌ **{embed_name}** adlı embed bulunamadı!")
        return
    
    embeds[embed_name]["description"] = description
    save_guild_embeds(guild_id, embeds)

    await ctx.send(f"✅ **{embed_name}** açıklaması ayarlandı!")

# Embed rengini ayarlama komutu
@bot.command()
@commands.has_permissions(manage_messages=True)
async def embed_color(ctx, embed_name, color: str):
    guild_id = ctx.guild.id
    embeds = get_guild_embeds(guild_id)

    if embed_name not in embeds:
        await ctx.send(f"❌ **{embed_name}** adlı embed bulunamadı!")
        return
    
    if not color.startswith("#") or len(color) != 7:
        await ctx.send("❌ **Hex renk kodu hatalı!** Örnek: `#ff0000`")
        return

    embeds[embed_name]["color"] = color
    save_guild_embeds(guild_id, embeds)

    await ctx.send(f"✅ **{embed_name}** rengi **{color}** olarak ayarlandı!")

# Embed görsel ekleme komutu
@bot.command()
@commands.has_permissions(manage_messages=True)
async def embed_image(ctx, embed_name, image_url: str):
    guild_id = ctx.guild.id
    embeds = get_guild_embeds(guild_id)

    if embed_name not in embeds:
        await ctx.send(f"❌ **{embed_name}** adlı embed bulunamadı!")
        return
    
    embeds[embed_name]["image"] = image_url
    save_guild_embeds(guild_id, embeds)

    await ctx.send(f"✅ **{embed_name}** için görsel ayarlandı!")

# Embed gönderme komutu
@bot.command()
@commands.has_permissions(manage_messages=True)
async def embed_send(ctx, embed_name):
    guild_id = ctx.guild.id
    embeds = get_guild_embeds(guild_id)

    if embed_name not in embeds:
        await ctx.send(f"❌ **{embed_name}** adlı embed bulunamadı!")
        return
    
    data = embeds[embed_name]

    embed = discord.Embed(
        title=data["title"],
        description=data["description"],
        color=int(data["color"][1:], 16)  # HEX renk kodunu sayıya çeviriyoruz
    )

    if data["image"]:
        embed.set_image(url=data["image"])

    await ctx.send(embed=embed)

bot.run(TOKEN)
