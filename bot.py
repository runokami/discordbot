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

def load_server_data():
    try:
        with open("server_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_server_data(data):
    with open("server_data.json", "w") as f:
        json.dump(data, f)

def get_server_embed_settings(guild_id):
    data = load_server_data()
    guild_id = str(guild_id)
    if guild_id not in data:
        data[guild_id] = {}
    return data[guild_id]

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
        color = discord.Color.from_str(color)
    except ValueError:
        color = discord.Color.blue()

    embed = discord.Embed(
        title=title.content,
        description=description.content,
        color=color
    )

    await ctx.send(embed=embed)

bot.run(TOKEN)
