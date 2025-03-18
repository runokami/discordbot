import discord
from discord.ext import commands
import re
import os

TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = discord.app_commands.CommandTree(bot) # Burası sadece bir defa olmalı

def hex_to_int(hex_code):
    hex_code = hex_code.lstrip("#")
    return int(hex_code, 16)

@bot.command(name="embed create")
async def embed_create(ctx, başlık: str, açıklama: str, renk: str = "#00FF00", görsel_url: str = None, footer_metni: str = None):
    # ... (komut kodları)

@tree.command(name="embed_create", description="Yeni bir embed oluşturur.")
async def embed_create_slash(interaction: discord.Interaction, başlık: str, açıklama: str, renk: str = "#00FF00", görsel_url: str = None, footer_metni: str = None):
    # ... (komut kodları)

@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yaptık!")
    await tree.sync()

bot.run(TOKEN)
