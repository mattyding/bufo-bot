import os
import random

import discord
from discord.ext import commands

from util import *
from commands import *
from bufo_nn import *
from bufo_nn import BufoNN

TOKEN = os.getenv("DISCORD_TOKEN")

client = init()
macros = load_macros()
messages = []
message_generator = BufoNN()


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # sanitize message content
    message.content = sanitize(message.content)

    messages.append(message.content)

    await macro_cmd(message)  # check for macros

    if message.content.startswith("$list macros"):
        await message.channel.send("Available macros: " + ", ".join(macros.keys()))
    if message.content.startswith("$bufo"):
        await bufo_cmd(message)
    if message.content.startswith("$bufo go away"):
        await message.guild.voice_client.disconnect()

    # Train the neural network (you need to implement this method)
    input_text = ...  # Get the input text from the message
    output_text = ...  # Get the expected output text from the message
    message_generator.train(input_text, output_text)

    # Generate a response and send it
    response = message_generator.generate_response(input_text)
    await message.channel.send(response)


# Create a bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

client.run(TOKEN)
