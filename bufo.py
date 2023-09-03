# bot.py
import os
import random
from collections import defaultdict

import discord
from dotenv import load_dotenv
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

client = discord.Client(intents=intents)

macros = defaultdict(list)
with open("macros.csv", "r") as f:
    f.readline()
    for line in f:
        line = line.split(",")
        macros[line[0]].append(line[1])


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    await macro_cmd(message)  # check for macros

    if message.content.startswith("$list macros"):
        await message.channel.send("Available macros: " + ", ".join(macros.keys()))
    if message.content.startswith("$bufo"):
        await bufo_cmd(message)
    if message.content.startswith("$bufo go away"):
        await message.guild.voice_client.disconnect()


async def macro_cmd(message):
    # remove all punctuation
    message.content = "".join([c for c in message.content if c.isalpha() or c == " "])
    words = message.content.lower().split()
    candidates = []
    for macro in macros:
        if macro in words:
            candidates += macros[macro]
        print(candidates)
    print("\n")
    if candidates:
        await message.channel.send(random.choice(candidates))


async def bufo_cmd(message):
    if message.author.voice:
        voice_channel = message.author.voice.channel
        if message.guild.voice_client is None:
            await voice_channel.connect()
        elif message.guild.voice_client.channel != voice_channel:
            await message.guild.voice_client.move_to(voice_channel)
    if message.guild.voice_client.is_playing():
        message.guild.voice_client.stop()


# Create a bot instance
bot = commands.Bot(command_prefix="!", intents=intents)


client.run(TOKEN)
