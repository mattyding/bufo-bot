from argparse import Namespace
from discord import Message
from bufo.constants import PERSONA_TO_ID_MAPPING_FILE
from bufo.utils import get_logger
from bufo.handlers.command_handler import BotCommandHandler

logger = get_logger(__name__)

ALL_COMMANDS = [
    "help", "connect", "disconnect (go away)", "enable", "disable",
    "persona (simulate, mode)"
]


def init_commands(handler: BotCommandHandler):
    handler.add_cmd("help")

    def bufo_help(bot_state: 'BufoBot', message: Message, args: Namespace):
        return f"Available commands: {','.join(ALL_COMMANDS)}"

    handler.map_cmd_to_fn("help", bufo_help)

    handler.add_cmd("connect")
    handler.add_cmd("disconnect")
    handler.add_cmd("go away", alias_for="disconnect")

    async def bufo_connect(bot_state: 'BufoBot', message: Message,
                           args: Namespace):
        if message.author.voice:
            voice_channel = message.author.voice.channel
            if message.guild.voice_client is None:
                await voice_channel.connect()
            elif message.guild.voice_client.channel != voice_channel:
                await message.guild.voice_client.move_to(voice_channel)

    async def bufo_disconnect(bot_state: 'BufoBot', message: Message,
                              args: Namespace):
        if message.guild.voice_client is not None:
            await message.guild.voice_client.disconnect()

    handler.map_cmd_to_fn("connect", bufo_connect, is_async=True)
    handler.map_cmd_to_fn("disconnect", bufo_disconnect, is_async=True)

    handler.add_cmd("enable")
    handler.add_cmd("disable")

    def _enable(bot_state: 'BufoBot', message: Message, args: Namespace):
        bot_state.cfg.enable_responses = True
        logger.info("Message responses enabled")

    def _disable(bot_state: 'BufoBot', message: Message, args: Namespace):
        bot_state.cfg.enable_responses = False
        logger.info("Message responses disabled")

    handler.map_cmd_to_fn("enable", _enable)
    handler.map_cmd_to_fn("disable", _disable)

    persona_args = handler.add_cmd("persona")
    handler.add_cmd("simulate", alias_for="persona")
    handler.add_cmd("mode", alias_for="persona")

    persona_args.add_argument("name",
                              type=str,
                              help="Name of the persona to enable")

    async def bufo_persona(bot_state: 'BufoBot', message: Message,
                           args: Namespace):
        import json
        with open(PERSONA_TO_ID_MAPPING_FILE) as f:
            persona_to_id = json.load(f)
        if args.name not in persona_to_id:
            return f"Persona {args.name} not found. Available personas: {', '.join(persona_to_id.keys())}"
        bot_state.cfg.persona = args.name
        logger.info(f"Persona set to {args.name}")
        return f"Ribbit! I am now {args.name}!"

    handler.map_cmd_to_fn("persona", bufo_persona, is_async=True)
