import discord
from discord.ext import commands
import re
import os

TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = discord.app_commands.CommandTree(bot)

def hex_to_int(hex_code):
    hex_code = hex_code.lstrip("#")
    return int(hex_code, 16)

@bot.command(name="embed create")
async def embed_create(ctx, başlık: str, açıklama: str, renk: str = "#00FF00", görsel_url: str = None, footer_metni: str = None):
    if not re.match(r'^#([0-9A-Fa-f]{6})$', renk):
        await ctx.send("Geçersiz renk kodu. #ffffff formatında bir hex renk kodu girin.")
        return

    color = hex_to_int(renk)
    embed = discord.Embed(title=başlık, description=açıklama, color=color)
    if görsel_url:
        embed.set_image(url=görsel_url)
    if footer_metni:
        embed.set_footer(text=footer_metni)

    await ctx.send(embed=embed)

@tree.command(name="embed_create", description="Embed create komutunu kullanın.")
async def embed_create_slash(interaction: discord.Interaction, başlık: str, açıklama: str, renk: str = "#00FF00", görsel_url: str = None, footer_metni: str = None):
    if not re.match(r'^#([0-9A-Fa-f]{6})$', renk):
        await interaction.response.send_message("Geçersiz renk kodu. #ffffff formatında bir hex renk kodu girin.", ephemeral=True)
        return

    color = hex_to_int(renk)
    embed = discord.Embed(title=başlık, description=açıklama, color=color)
    if görsel_url:
        embed.set_image(url=görsel_url)
    if footer_metni:
        embed.set_footer(text=footer_metni)

    await interaction.response.send_message(embed=embed)

@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yaptık!")
    await tree.sync()

bot.run(TOKEN)
