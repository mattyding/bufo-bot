# File containing util functions.
import discord
from collections import defaultdict
from dotenv import load_dotenv


def init():
    load_dotenv()

    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True
    intents.message_content = True
    return discord.Client(intents=intents)


def load_macros():
    macros = defaultdict(list)
    with open("macros.csv", "r") as f:
        f.readline()
        for line in f:
            line = line.split(",")
            macros[line[0]].append(line[1])
    return macros


def sanitize(message):
    return "".join([c for c in message if c.isalpha() or c == " "]).lower()
