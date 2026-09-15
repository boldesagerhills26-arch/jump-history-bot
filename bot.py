import os
import asyncio
import discord
from discord.ext import commands
from flask import Flask, request
from threading import Thread

TOKEN = os.getenv("DISCORD_TOKEN")

CATEGORY_ID = 1549547532013674526

app = Flask(__name__)

intents = discord.Intents.default()
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


@app.route("/")
def home():
    return "Jump History Bot is running!"


@app.route("/jump", methods=["POST"])
def jump():
    data = request.get_json(silent=True)

    if not data:
        return "Missing data", 400

    result = data.get("result", "Ingen resultatdata.")
    number = data.get("number")

    asyncio.run_coroutine_threadsafe(
        create_jump_channel(result, number),
        bot.loop
    )

    return "OK", 200


async def create_jump_channel(result, number=None):
    guild = None

    for g in bot.guilds:
        category = g.get_channel(CATEGORY_ID)

        if category and isinstance(category, discord.CategoryChannel):
            guild = g
            break

    if guild is None:
        print("Kunne ikke finde JUMP HISTORIK-kategorien.")
        return

    category = guild.get_channel(CATEGORY_ID)

    if number is None:
        existing_numbers = []

        for channel in category.channels:
            if channel.name.isdigit() and len(channel.name) == 5:
                existing_numbers.append(int(channel.name))

        if existing_numbers:
            number = max(existing_numbers) + 1
        else:
            number = 1

    channel_name = f"{number:05d}"

    existing = discord.utils.get(category.channels, name=channel_name)

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


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Jump History Bot is ready!")


def run_webserver():
    app.run(host="0.0.0.0", port=10000)


Thread(target=run_webserver, daemon=True).start()

bot.run(TOKEN)
