import logging
import os
import sys
import json
import random

from typing import Optional

from discord.ext import commands
from dotenv import load_dotenv

import utils as utils


class Bot:
    def __init__(self):
        load_dotenv()
        self.token = os.getenv("DISCORD_TOKEN")
        self.parser = utils.init_parser()
        self.mode = "default"
        self.enable_responses = True

    async def on_ready(self):
        self.tt_random_response = 0
        logging.info(f"Bufo buddy has connected to Discord!")

    async def on_message(self, message):
        # discard all messages from bots
        logging.info(f"Received message: {message.content}")
        if message.author.bot:
            return
        if message.content.lower().startswith("$bufo"):
            await self.process_command(message)
            
        response = await self.maybe_respond(message)
        if response is not None:
            logging.info("Response: " + response)
            await message.channel.send(response)

    async def process_command(self, message):
        cmd, params = self.parser.parse_params(message.content)
        env_params = self.parser.get_env_params(cmd)
        if "slf" in env_params:
            params.update({"slf": self})
        if "message" in env_params:
            params.update({"message": message})
        try:
            await self.parser.execute(cmd, params)
        except ValueError as e:
            await message.channel.send(
                f"Error encountered in command {cmd}:\n\t{str(e)}"
            )

    async def maybe_respond(self, message) -> Optional[str]:
        """
        If mode is set, generates response using files in mode directory.
        - mode/ directory contains (optional) prefix.jsonl and (required) response.txt files
        - prefix jsonl maps prefix strings to a list of responses for that prefix. One prefix per line
        - response.txt contains one response per line
        """
        if not self.enable_responses:
            return
        
        # if prefix match, always respond
        prefix_file = os.path.join("persona", self.mode, "prefix.jsonl")
        if os.path.exists(prefix_file):
            with open(prefix_file) as f:
                for line in f:
                    prefix_data = json.loads(line)
                    for prefix, responses in prefix_data.items():
                        if message.content.lower().startswith(prefix.lower()):
                            response = random.choice(responses)
                            return response
                        
        # otherwise, wait for TTL to respond
        if self.tt_random_response > 0:
            self.tt_random_response -= 1
            return
        self.tt_random_response = random.randint(0, 2)

        response_file = os.path.join("persona", self.mode, "response.txt")
            
        with open(response_file) as f:
            responses = f.readlines()
        
        if responses:
            response = random.choice(responses).strip()
            return response

    def run(self):
        try:
            bot = commands.Bot(command_prefix="!", intents=utils.load_intents())
            bot.add_listener(self.on_ready)
            bot.add_listener(self.on_message)
            bot.run(self.token)
        except KeyboardInterrupt:
            logging.info("Received SIGINT, exiting...")
            sys.exit(0)


if __name__ == "__main__":
    utils.setup_logging()
    bot = Bot()
    bot.run()
