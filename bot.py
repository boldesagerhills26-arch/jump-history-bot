import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

TOKEN = os.getenv("DISCORD_TOKEN")

app = Flask(__name__)

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@app.route("/")
def home():
    return "Jump History Bot is running!"


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Jump History Bot is ready!")


def run_webserver():
    app.run(host="0.0.0.0", port=10000)


Thread(target=run_webserver, daemon=True).start()

bot.run(TOKEN)
