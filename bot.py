import os
import re
import asyncio
import urllib.parse
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

TOKEN = os.getenv("DISCORD_TOKEN")

CATEGORY_ID = 1549547532013674526

app = Flask(__name__)

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@app.route("/")
def home():
    return "Jump History Bot is running!"


async def create_jump_channel(message, number):
    for guild in bot.guilds:
        category = guild.get_channel(CATEGORY_ID)

        if not category or not isinstance(category, discord.CategoryChannel):
            continue

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

        # Find spillere og antal navne
        pattern = r"<@!?(\d+)>\s+—\s+\*\*(\d+)\s+navne?\*\*"
        matches = re.findall(pattern, message.content)

        wheel_entries = []

        for user_id, amount in matches:
            try:
                member = await guild.fetch_member(int(user_id))
                name = member.display_name
            except:
                name = f"Spiller {user_id}"

            for _ in range(int(amount)):
                wheel_entries.append(name)

        # Lav Wheel of Names-link
        wheel_link = None

        if wheel_entries:
            entries = ",".join(wheel_entries)
            encoded_entries = urllib.parse.quote(entries)

            wheel_link = (
                "https://wheelofnames.com/"
                "?entries=" + encoded_entries
            )

        # Lav samlet besked
        content = message.content

        if wheel_link:
            content += (
                "\n\n🎡 **JUMP HJUL**\n"
                f"👉 [**ÅBN HJUL**]({wheel_link})"
            )

        # Send resultat + hjul i SAMME besked
        await channel.send(content)

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

    # Vi reagerer kun på bot-beskeder
    if not message.author.bot:
        return

    # Skal være et jump-resultat
    if "JUMP #" not in message.content:
        return

    match = re.search(r"JUMP #(\d+)", message.content)

    if not match:
        return

    number = int(match.group(1))

    asyncio.create_task(
        create_jump_channel(message, number)
    )


def run_webserver():
    app.run(host="0.0.0.0", port=10000)


Thread(target=run_webserver, daemon=True).start()

bot.run(TOKEN)
