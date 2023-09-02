# bot.py
import os

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

macros = {}
with open("macros.csv", "r") as f:
    f.readline()
    for line in f:
        line = line.strip()
        if line:
            macro, say = line.split(",")
            macros[macro] = say


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    for macro in macros:
        if macro in message.content:
            await message.channel.send(macros[macro])

    if message.content.startswith("$bufo"):
        if message.author.voice:
            voice_channel = message.author.voice.channel
            if message.guild.voice_client is None:
                await voice_channel.connect()
            elif message.guild.voice_client.channel != voice_channel:
                await message.guild.voice_client.move_to(voice_channel)
        if message.guild.voice_client.is_playing():
            message.guild.voice_client.stop()

    if message.content.startswith("$bufo go away"):
        await message.guild.voice_client.disconnect()


# Create a bot instance
bot = commands.Bot(command_prefix="!", intents=intents)


client.run(TOKEN)
