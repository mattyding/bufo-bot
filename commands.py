# File containing code for bot commands.
from utils import DATASET_FILE

import utils as utils


async def parse_cmd(cmd, args, message, bot):
    if cmd == "join":
        await bufo_connect(message)
    if cmd == "goaway":
        await bufo_disconnect(message)
    if cmd == "train":
        await bufo_train_model(bot, args, message)


async def bufo_connect(message):
    if message.author.voice:
        voice_channel = message.author.voice.channel
        if message.guild.voice_client is None:
            await voice_channel.connect()
        elif message.guild.voice_client.channel != voice_channel:
            await message.guild.voice_client.move_to(voice_channel)


async def bufo_disconnect(message):
    if message.guild.voice_client is not None:
        await message.guild.voice_client.disconnect()


async def bufo_train_model(bot, args, message):
    with open(DATASET_FILE, "r") as f:
        lines = f.readlines()
    training_pairs = []
    for line in lines:
        try:
            input_text, output_text = line.split("\t")
        except ValueError:
            print("Bad line: " + line)
            continue
        training_pairs.append((input_text, output_text))
    utils.copy_corpus()
    bot.model.train(training_pairs, num_epochs=7)
    bot.corpus = utils.load_corpus()
    bot.append_corp = set()
    await message.channel.send(
        "Training complete! Bufo AI is ready to take over the world :frog:"
    )
