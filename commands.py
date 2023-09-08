# File containing code for bot commands.
from utils import DATASET_FILE

import utils as utils

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


async def bufo_train_model(model, epochs, batch_size, lr, message):
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
    model.model.train(training_pairs, num_epochs=epochs, batch_size=batch_size, lr=lr)
    model.corpus = utils.load_corpus()
    model.append_corp = set()
    await message.channel.send(
        "Training complete! Bufo AI is ready to take over the world :frog:"
    )
