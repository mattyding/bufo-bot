import os

import discord
from discord.ext import commands

from util import *
from commands import *
from bufo_nn import *
from bufo_nn import BufoNN

init()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = load_intents()
client = discord.Client(intents=intents)
macros = load_macros()
words = load_words()

# store state of previous message for training
prev_msg = [""]
model = [None]


@client.event
async def on_ready():
    model[0] = BufoNN()
    print(f"{client.user} has connected to Discord!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # sanitize message content
    log_msg(message, words, prev_msg)

    # await macro_cmd(message, macros)  # check for macros

    if message.content.startswith("$list macros"):
        await message.channel.send("Available macros: " + ", ".join(macros.keys()))
    if message.content.startswith("$bufo"):
        await bufo_cmd(message)
    if message.content.startswith("$bufo go away"):
        await message.guild.voice_client.disconnect()
    if message.content.startswith("$bufo train"):
        model[0] = BufoNN()
        train_cmd(model[0])
        await message.channel.send(
            "Training complete! Bufo AI is ready to take over the world :frog:"
        )
    if message.content.startswith("$bufo infer"):
        # Generate a response and send it
        response = model[0].predict(sanitize(message.content.split("$bufo infer ")[1]))
        await message.channel.send(response)


# Create a bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

client.run(TOKEN)
