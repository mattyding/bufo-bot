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
