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

bot.run(TOKEN)
