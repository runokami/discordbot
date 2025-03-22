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

import discord
from discord.ext import commands
from discord import app_commands
import json
import os

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
        color = discord.Color.from_str
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

bot.run(TOKEN)
