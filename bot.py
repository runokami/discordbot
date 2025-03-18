import discord
import json
import os

TOKEN = os.environ.get("DISCORD_TOKEN") # GitHub Actions'tan token al
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

EMBEDS_FILE = "embeds.json"

def load_embeds():
    try:
        with open(EMBEDS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_embeds(embeds):
    with open(EMBEDS_FILE, "w") as f:
        json.dump(embeds, f, indent=4)

@client.event
async def on_ready():
    print(f"{client.user} olarak giriş yaptık!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!embed create"):
        parts = message.content.split(" ")
        if len(parts) < 3:
            await message.channel.send("Kullanım: !embed create <ad> [renk]")
            return

        embed_name = parts[2]
        color = 0x00FF00  # Varsayılan renk (yeşil)
        if len(parts) > 3:
            try:
                color = int(parts[3], 16)
            except ValueError:
                await message.channel.send("Geçersiz renk kodu. Hex renk kodu girin (örneğin, 0xFF0000).")
                return

        embeds = load_embeds()
        embeds[embed_name] = {"color": color}
        save_embeds(embeds)
        await message.channel.send(f"'{embed_name}' adında embed oluşturuldu. Renk: {hex(color)}")

    elif message.content.startswith("!embed list"):
        embeds = load_embeds()
        if not embeds:
            await message.channel.send("Kayıtlı embed yok.")
            return

        embed_list = "\n".join(f"- {name}: {hex(data['color'])}" for name, data in embeds.items())
        await message.channel.send(f"Kayıtlı Embedler:\n{embed_list}")

    elif message.content.startswith("!gönder"):
        parts = message.content.split(" ")
        if len(parts) < 2:
            await message.channel.send("Kullanım: !gönder <ad>")
            return
        embed_name = parts[1]
        embeds = load_embeds()
        if embed_name not in embeds:
            await message.channel.send("Embed bulunamadı.")
            return
        embed_data = embeds[embed_name]
        embed = discord.Embed(title=embed_name, color=embed_data["color"])
        await message.channel.send(embed=embed)

    elif message.content.startswith("!help"):
        help_message = """
        Komutlar:
        - !embed create <ad> [renk]: Yeni bir embed oluşturur.
        - !embed list: Kayıtlı embedleri listeler.
        - !gönder <ad>: Belirtilen embedi gönderir.
        - !help: Bu yardım mesajını gösterir.
        """
        await message.channel.send(help_message)

client.run(TOKEN)
