# File containing code for bot commands.


async def macro_cmd(message):
    # remove all punctuation
    words = message.content.split(" ")
    candidates = []
    for macro in macros:
        if macro in words:
            candidates += macros[macro]
        print(candidates)
    print("\n")
    if candidates:
        await message.channel.send(random.choice(candidates))


async def bufo_cmd(message):
    if message.author.voice:
        voice_channel = message.author.voice.channel
        if message.guild.voice_client is None:
            await voice_channel.connect()
        elif message.guild.voice_client.channel != voice_channel:
            await message.guild.voice_client.move_to(voice_channel)
    if message.guild.voice_client.is_playing():
        message.guild.voice_client.stop()
