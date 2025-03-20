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

@bot.tree.command(name="embed", description="Bir embed mesajı gönderir.")
async def embed_slash(interaction: discord.Interaction):
    embed = create_embed(
        title="Embed Başlığı (Slash Komutu)",
        description="Bu bir embed mesajıdır (slash komutu ile gönderildi).",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@bot.command()
async def embed_text(ctx):
    embed = create_embed(
        title="Embed Başlığı (Metin Komutu)",
        description="Bu bir embed mesajıdır (metin komutu ile gönderildi).",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)

bot.run(TOKEN)
