import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

TOKEN = os.getenv("DISCORD_TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "Jump History Bot is running!"

def run():
    app.run(host="0.0.0.0", port=10000)

Thread(target=run).start()

intents = discord.Intents.default()
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
