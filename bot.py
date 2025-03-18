import discord
import json
import os
import re

TOKEN = os.environ.get("DISCORD_TOKEN")
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

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

def hex_to_int(hex_code):
    hex_code = hex_code.lstrip("#")
    return int(hex_code, 16)

@client.event
async def on_ready():
    print(f"{client.user} olarak giriş yaptık!")
    await tree.sync()

@tree.command(name="embed_oluştur", description="Yeni bir embed oluşturur.")
async def create_embed(interaction: discord.Interaction, ad: str, başlık: str, açıklama: str, renk: str = "#00FF00", görsel_url: str = None, footer_metni: str = None):
    if not re.match(r'^#([0-9A-Fa-f]{6})$', renk):
        await interaction.response.send_message("Geçersiz renk kodu. #ffffff formatında bir hex renk kodu girin.", ephemeral=True)
        return

    color = hex_to_int(renk)
    embeds = load_embeds()
    embeds[ad] = {
        "başlık": başlık,
        "açıklama": açıklama,
        "renk": color,
        "görsel_url": görsel_url,
        "footer_metni": footer_metni,
        "oluşturan": interaction.user.id
    }
    save_embeds(embeds)
    await interaction.response.send_message(f"'{ad}' adında embed oluşturuldu.")

@tree.command(name="embed_listele", description="Kayıtlı embedleri listeler.")
async def list_embeds(interaction: discord.Interaction):
    embeds = load_embeds()
    if not embeds:
        await interaction.response.send_message("Kayıtlı embed yok.", ephemeral=True)
        return

    embed_list = "\n".join(f"- {name}: {data['başlık']}" for name, data in embeds.items())
    await interaction.response.send_message(f"Kayıtlı Embedler:\n{embed_list}")

@tree.command(name="gönder", description="Belirtilen embedi gönderir.")
async def send_embed(interaction: discord.Interaction, ad: str):
    embeds = load_embeds()
    if ad not in embeds:
        await interaction.response.send_message("Embed bulunamadı.", ephemeral=True)
        return

    embed_data = embeds[ad]
    embed = discord.Embed(title=embed_data["başlık"], description=embed_data["açıklama"], color=embed_data["renk"])
    if embed_data.get("görsel_url"):
        embed.set_image(url=embed_data["görsel_url"])
    if embed_data.get("footer_metni"):
        embed.set_footer(text=embed_data["footer_metni"], icon_url=interaction.user.avatar.url)
    oluşturan = await client.fetch_user(embed_data["oluşturan"])
    embed.set_author(name=oluşturan.name, icon_url=oluşturan.avatar.url)

    await interaction.response.send_message(embed=embed)

@tree.command(name="embed_renk_değiştir", description="Bir embedin rengini değiştirir.")
async def change_embed_color(interaction: discord.Interaction, ad: str, yeni_renk: str):
    if not re.match(r'^#([0-9A-Fa-f]{6})$', yeni_renk):
        await interaction.response.send_message("Geçersiz renk kodu. #ffffff formatında bir hex renk kodu girin.", ephemeral=True)
        return

    embeds = load_embeds()
    if ad not in embeds:
        await interaction.response.send_message("Embed bulunamadı.", ephemeral=True)
        return

    color = hex_to_int(yeni_renk)
    embeds[ad]["renk"] = color
    save_embeds(embeds)
    await interaction.response.send_message(f"'{ad}' embedinin rengi {yeni_renk} olarak değiştirildi.")

@tree.command(name="yardım", description="Komutları gösterir.")
async def help_command(interaction: discord.Interaction):
    help_message = """
    Komutlar:
    - /embed_oluştur <ad> <başlık> <açıklama> [renk] [görsel_url] [footer_metni]: Yeni bir embed oluşturur.
    - /embed_listele: Kayıtlı embedleri listeler.
    - /gönder <ad>: Belirtilen embedi gönderir.
    - /embed_renk_değiştir <ad> <yeni_renk>: Bir embedin rengini değiştirir.
    - /yardım: Bu yardım mesajını gösterir.
    """
    await interaction.response.send_message(help_message)

client.run(TOKEN)
