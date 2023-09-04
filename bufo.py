import os
import signal
import sys

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
corpus = load_corpus()

# store state of previous message for training
prev_msg = [""]
model = [None]


@client.event
async def on_ready():
    model[0] = BufoNN()
    print(f"{client.user} has connected to Discord!")


def handle_ctrl_c(signal, frame):
    # trigger model[0]__del__() to save weights
    model[0] = None
    sys.exit(0)


# Register the Ctrl+C signal handler
signal.signal(signal.SIGINT, handle_ctrl_c)


@client.event
async def on_message(message):
    # discard all messages from bots
    if message.author.bot:
        return

    # sanitize message content
    new_words = log_msg(message, corpus, prev_msg)

    # await macro_cmd(message, macros)  # check for macros

    if message.content.startswith("$list macros"):
        await message.channel.send("Available macros: " + ", ".join(macros.keys()))
    if message.content.startswith("$bufo"):
        await bufo_cmd(message)
    if message.content.startswith("$bufo go away"):
        await message.guild.voice_client.disconnect()
    if message.content.startswith("$bufo train"):
        epochs = (
            int(message.content.split("--epochs=")[1])
            if "--epochs" in message.content
            else 1
        )
        model[0] = BufoNN()
        train_cmd(model[0], epochs=epochs)
        await message.channel.send(
            "Training complete! Bufo AI is ready to take over the world :frog:"
        )
    if not new_words:
        response = model[0].predict(sanitize(message.content))
        if response:
            await message.channel.send(response)


# Create a bot instance
try:
    bot = commands.Bot(command_prefix="!", intents=intents)
    client.run(TOKEN)
except KeyboardInterrupt:
    pass
