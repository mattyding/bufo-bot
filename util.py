# File containing util functions.
import discord
from collections import defaultdict
from dotenv import load_dotenv

CORPUS_FILE = "data/corpus.txt"


def init():
    load_dotenv()


def load_intents():
    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True
    intents.message_content = True
    return intents


def load_macros():
    macros = defaultdict(list)
    with open("macros.csv", "r") as f:
        f.readline()
        for line in f:
            line = line.split(",")
            macros[line[0]].append(line[1])
    return macros


def load_words():
    return set(open(CORPUS_FILE, "r").read().splitlines())


def write_word(word):
    with open(CORPUS_FILE, "a") as f:
        f.write(word + "\n")


def sanitize(message):
    return "".join([c for c in message if c.isalpha() or c == " "]).lower()


def log_msg(message, words, prev_msg):
    message = sanitize(message.content)
    if "bufo" in message:
        # don't log commands
        return
    for word in message.split():
        if word not in words:
            words.add(word)
            write_word(word)
    input_text = prev_msg[0]
    output_text = message
    # store all pairs in a dataset file
    if prev_msg[0] != "":
        with open("data/dataset.txt", "a") as f:
            f.write(f"{input_text}\t{output_text}\n")
    prev_msg[0] = output_text
