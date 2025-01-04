# File containing util functions.
import discord


def load_intents():
    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True
    intents.message_content = True
    return intents
