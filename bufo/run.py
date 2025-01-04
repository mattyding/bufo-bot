import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from bufo.handlers import BotCommandHandler, UserMessageHandler
from bufo.commands import init_commands

from utils import get_logger, log_user_msg_to_file, load_intents
from bufo.constants import COMMAND_PREFIX

logger = get_logger(__name__)


class BufoBotConfig(BaseModel):
    enable_responses: bool = Field(default=True)
    persona: str = Field(default="default")


class BufoBot:

    def __init__(self, config: BufoBotConfig):
        load_dotenv()

        self.cfg = config

        self.command_handler = BotCommandHandler(self.cfg)
        init_commands(self.command_handler)
        self.response_handler = UserMessageHandler(self.cfg)

    async def on_ready(self):
        logging.info(f"Bufo buddy has connected to Discord!")

    async def on_message(self, message: discord.Message):
        logging.info(f"Received message: {message.content}")
        # discard all messages from bots
        if message.author.bot:
            return
        if message.content.lower().startswith(COMMAND_PREFIX):
            response = await self.command_handler.handle(bot_state=self,
                                                         message=message)
        else:
            log_user_msg_to_file(message)
            response = await self.response_handler.handle(bot_state=self,
                                                          message=message)

        if response:
            logging.info(f"Response: {response}")
            await message.channel.send(response)

    def run(self):
        bot = commands.Bot(command_prefix="!", intents=load_intents())
        bot.add_listener(self.on_ready)
        bot.add_listener(self.on_message)
        bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    bot = BufoBot(BufoBotConfig())
    bot.run()
