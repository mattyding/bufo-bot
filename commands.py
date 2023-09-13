# File containing code for bot commands.


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


async def bufo_train_model(model, epochs, batch_size, lr):
    with open("data/dataset.txt", "r") as f:
        lines = f.readlines()
    training_pairs = []
    for line in lines:
        try:
            input_text, output_text = line.split("\t")
        except ValueError:
            print("Bad line: " + line)
            continue
        training_pairs.append((input_text, output_text))
    model.train(training_pairs, num_epochs=epochs, batch_size=batch_size, lr=lr)
    raise ValueError(  # hacky way of sending msg to channel
        "Training complete! Bufo AI is ready to take over the world :frog:"
    )
