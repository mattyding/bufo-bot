import logging
import os
import sys

from discord.ext import commands
from dotenv import load_dotenv

import commands as bufo_cmds
import utils as utils
from seq2seq import BufoSeq2Seq


class Bot:
    def __init__(self):
        load_dotenv()
        self.token = os.getenv("DISCORD_TOKEN")
        self.corpus = utils.load_corpus()
        self.append_corp = set()
        self.parser = utils.init_parser()
        self.enable_responses = True

        # store state of previous message for training
        self.prev_msg = ""
        self.model = BufoSeq2Seq()

    # def handle_ctrl_c(self, signal, frame):
    #     # trigger model.__del__() to save weights
    #     sys.exit(0)

    async def on_ready(self):
        self.model = BufoSeq2Seq()
        logging.info(f"Bufo buddy has connected to Discord!")

    async def on_message(self, message):
        # discard all messages from bots
        if message.author.bot:
            return
        if message.content.lower().startswith("$bufo"):
            await self.process_command(message)
        if self.log_message(message):
            # don't log commands
            self.log_msg(message)
            response = self.model.predict(message.content)
            if self.enable_responses and response:
                await message.channel.send(response)

    def log_message(self, message):
        blocklist = [
            "$bufo",
            "https://youtube.com",
            "https://youtu.be",
            "https://tiktok.com",
        ]
        for prefix in blocklist:
            if message.content.lower().startswith(prefix):
                return False
        return True

    async def process_command(self, message):
        cmd, params = self.parser.parse_params(message.content)
        env_params = self.parser.get_env_params(cmd)
        if "slf" in env_params:
            params.update({"slf": self})
        if "message" in env_params:
            params.update({"message": message})
        if "model" in env_params:
            params.update({"model": self.model})
        try:
            await self.parser.execute(cmd, params)
        except ValueError as e:
            await message.channel.send(str(e))

    def log_msg(self, message):
        sanitized_msg = utils.sanitize(message.content)
        if not sanitized_msg:
            return
        for word in sanitized_msg.split():
            if word not in self.corpus and word not in self.append_corp:
                utils.write_word_to_append_file(word)
                self.append_corp.add(word)
        if self.prev_msg != "":
            utils.write_training_example(self.prev_msg, sanitized_msg)
        self.prev_msg = sanitized_msg

    def run(self):
        try:
            bot = commands.Bot(command_prefix="!", intents=utils.load_intents())
            bot.add_listener(self.on_ready)
            bot.add_listener(self.on_message)
            bot.run(self.token)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    utils.setup_logging()
    bot = Bot()
    bot.run()
