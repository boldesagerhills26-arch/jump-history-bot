import os
import re
import urllib.parse
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

TOKEN = os.getenv("DISCORD_TOKEN")

app = Flask(__name__)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@app.route("/")
def home():
    return "Jump Wheel Bot is running!"


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Jump Wheel Bot is ready!")


@bot.event
async def on_message(message):
    # Ignorer egne beskeder
    if message.author == bot.user:
        return

    # Vi leder kun efter bot-beskeder
    if not message.author.bot:
        return

    # Skal være et JUMP-resultat
    if "JUMP #" not in message.content:
        return

    # Find spillere og antal navne
    pattern = r"<@!?(\d+)>\s+—\s+\*\*(\d+)\s+navne?\*\*"
    matches = re.findall(pattern, message.content)

    if not matches:
        print("Fandt et JUMP-resultat, men ingen spillere.")
        return

    wheel_entries = []

    for user_id, amount in matches:
        try:
            member = await message.guild.fetch_member(int(user_id))
            name = member.display_name
        except:
            name = f"Spiller {user_id}"

        for _ in range(int(amount)):
            wheel_entries.append(name)

    # Lav Wheel of Names-link
    entries = ",".join(wheel_entries)
    encoded_entries = urllib.parse.quote(entries)

    wheel_link = (
        "https://wheelofnames.com/"
        "?entries=" + encoded_entries
    )

    # Send direkte under resultatet i SAMME kanal
    await message.channel.send(
        "🎡 **JUMP HJUL**\n"
        f"👉 [**ÅBN HJUL**]({wheel_link})"
    )

    print(f"Wheel oprettet: {entries}")


def run_webserver():
    app.run(host="0.0.0.0", port=10000)


Thread(target=run_webserver, daemon=True).start()

bot.run(TOKEN)
