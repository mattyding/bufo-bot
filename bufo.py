import logging
import os
import sys

from discord.ext import commands
from dotenv import load_dotenv

import commands as bufo_cmds
import utils as utils
from bufo_nn import BufoNN


class Bot:
    def __init__(self):
        load_dotenv()
        self.TOKEN = os.getenv("DISCORD_TOKEN")
        self.corpus = utils.load_corpus()
        self.append_corp = set()

        # store state of previous message for training
        self.prev_msg = ""
        self.model = BufoNN()

    def handle_ctrl_c(self, signal, frame):
        # trigger model.__del__() to save weights
        sys.exit(0)

    async def on_ready(self):
        self.model = BufoNN()
        logging.info(f"Bufo buddy has connected to Discord!")

    async def on_message(self, message):
        # discard all messages from bots
        if message.author.bot:
            return
        if message.content.lower().startswith("$bufo"):
            cmd, args = message.content.split()[1], message.content.split()[2:]
            await bufo_cmds.parse_cmd(cmd, args, message, self)
        else:
            # don't log commands
            self.log_msg(message)
            response = self.model.predict(message.content)
            if response:
                await message.channel.send(response)

    def log_msg(self, message):
        sanitized_msg = utils.sanitize(message.content)
        for word in sanitized_msg.split():
            if word not in self.corpus and word not in self.append_corp:
                utils.write_word_to_append_file(word)
        if self.prev_msg != "":
            utils.write_training_example(self.prev_msg, sanitized_msg)
        self.prev_msg = sanitized_msg

    def run(self):
        try:
            bot = commands.Bot(command_prefix="!", intents=utils.load_intents())
            bot.add_listener(self.on_ready)
            bot.add_listener(self.on_message)
            bot.run(self.TOKEN)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    utils.setup_logging()
    bot = Bot()
    bot.run()
