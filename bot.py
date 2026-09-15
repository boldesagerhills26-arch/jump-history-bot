import os
import re
import asyncio
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

TOKEN = os.getenv("DISCORD_TOKEN")

CATEGORY_ID = 1549547532013674526

app = Flask(__name__)

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@app.route("/")
def home():
    return "Jump History Bot is running!"


async def create_jump_channel(result, number):
    for guild in bot.guilds:
        category = guild.get_channel(CATEGORY_ID)

        if category and isinstance(category, discord.CategoryChannel):
            channel_name = f"{number:05d}"

            existing = discord.utils.get(
                category.channels,
                name=channel_name
            )

            if existing:
                channel = existing
            else:
                channel = await guild.create_text_channel(
                    channel_name,
                    category=category,
                    reason="Nyt jump afsluttet"
                )

            await channel.send(result)

            print(f"Oprettet jump-kanal #{channel_name}")
            return

    print("Kunne ikke finde JUMP HISTORIK-kategorien.")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Jump History Bot is ready!")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if not message.author.bot:
        return

    if "JUMP #" not in message.content:
        return

    match = re.search(r"JUMP #(\d+)", message.content)

    if not match:
        return

    number = int(match.group(1))

    asyncio.create_task(
        create_jump_channel(message.content, number)
    )


def run_webserver():
    app.run(host="0.0.0.0", port=10000)


Thread(target=run_webserver, daemon=True).start()

bot.run(TOKEN)
