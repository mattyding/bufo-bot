# File containing code for bot commands.
import random


async def macro_cmd(message, macros):
    # remove all punctuation
    words = message.content.split(" ")
    candidates = []
    for macro in macros:
        if macro in words:
            candidates += macros[macro]
    if candidates:
        await message.channel.send(random.choice(candidates))


async def bufo_cmd(message):
    if message.author.voice:
        voice_channel = message.author.voice.channel
        if message.guild.voice_client is None:
            await voice_channel.connect()
        elif message.guild.voice_client.channel != voice_channel:
            await message.guild.voice_client.move_to(voice_channel)
    # if message.guild.voice_client.is_playing():
    #     message.guild.voice_client.stop()


def train_cmd(model, epochs):
    with open("data/dataset.txt", "r") as f:
        lines = f.readlines()
    training_pairs = []
    for line in lines:
        input_text, output_text = line.split("\t")
        training_pairs.append((input_text, output_text))
    model.train(training_pairs, num_epochs=epochs)
