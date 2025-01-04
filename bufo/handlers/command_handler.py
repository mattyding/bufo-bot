import shlex
from argparse import ArgumentParser, Namespace, ArgumentError
from discord import Message
from typing import Protocol, Optional, Any, Dict, Callable
from dataclasses import dataclass

from bufo.handlers.base import AbstractHandler
from bufo.utils import get_logger

logger = get_logger(__name__)


class CommandFunction(Protocol):
    """Protocol for functions executed by command handlers"""

    async def __call__(self, bot_state: 'BufoBot', message: Message,
                       args: Namespace) -> Optional[str]:
        ...


@dataclass
class Command:
    name: str
    parser: ArgumentParser
    function: Optional[
        CommandFunction] = None  # while typing is optional, function is required
    alias_for: Optional[str] = None
    is_async: bool = False


class BotCommandHandler(AbstractHandler):
    """Handles bot command messages with $bufo prefix"""

    def __init__(self, cfg: Any):
        super().__init__(cfg)
        self.commands: Dict[str, Command] = {}
        self.validated = True

    def add_cmd(self,
                name: str,
                *,
                description: str = "",
                alias_for: Optional[str] = None) -> ArgumentParser:
        """
        Add a new command or alias to the handler
        
        Args:
            name: Name of the command (without prefix)
            description: Command description
            alias_for: If this is an alias, specify the original command name
            
        Returns:
            ArgumentParser for adding command arguments
        """
        if alias_for and alias_for not in self.commands:
            raise ValueError(
                f"Cannot create alias for non-existent command: {alias_for}")

        if alias_for:
            parser = self.commands[alias_for].parser
        else:
            parser = ArgumentParser(prog=name,
                                    description=description,
                                    exit_on_error=False)

        self.commands[name] = Command(name=name,
                                      parser=parser,
                                      alias_for=alias_for)
        self.validated = False

        return parser

    def map_cmd_to_fn(self,
                      command_name: str,
                      func: Callable,
                      is_async=False,
                      **kwargs):
        """
        Map a command to its handling function
        
        Args:
            command_name: Name of the command to map
            func: Function to call when command is invoked
            **kwargs: Additional arguments (e.g., async_fn=True)
        """
        if command_name not in self.commands:
            raise ValueError(
                f"Cannot map function to non-existent command: {command_name}")

        command = self.commands[command_name]
        command.function = func
        command.is_async = is_async
        self.validated = False

    def validate_commands(self):
        """Validates commands were set up correctly"""
        # all commands have a mapped functions
        for command in self.commands.values():
            if command.alias_for is None and not command.function:
                raise ValueError(
                    f"Command {command.name} has no mapped function")
        # check that all aliases point to valid commands
        for command in self.commands.values():
            if command.alias_for and command.alias_for not in self.commands:
                raise ValueError(
                    f"Alias {command.name} points to non-existent command: {command.alias_for}"
                )

        self.validated = True

    async def _execute_command(self, command: Command, args: Namespace,
                               bot_state: 'BufoBot',
                               message: Message) -> Optional[str]:
        """Execute the command function with parsed arguments"""
        try:
            if command.is_async:
                return await command.function(bot_state, message, args)
            else:
                return command.function(bot_state, message, args)
        except Exception as e:
            logger.error(f"Error executing command {command.name}: {str(e)}")
            return None

    async def handle(self, bot_state: 'BufoBot',
                     message: Message) -> Optional[str]:
        """
        Handle bot commands
        
        Args:
            bot_state: Reference to the bot instance
            message: Discord message object
            
        Returns:
            Optional response string
        """
        if not self.validated:
            self.validate_commands()

        parts = shlex.split(message.content)
        # parts[0] will be $bufo
        parts = parts[1:]
        if not parts:
            return None

        logger.info("Parts: " + str(parts))

        command_name = parts[0].lower()
        logger.info(f"Received command: {command_name}")

        command = self.commands.get(command_name)
        if not command:
            return "Invalid command. Type $bufo help for a list of commands."

        while command.alias_for:
            command = self.commands.get(command.alias_for)

        try:
            args = command.parser.parse_args(parts[1:])
        except ArgumentError as e:
            logger.error(
                f"Error parsing arguments for command {command_name}: {str(e)}"
            )
            return f"Invalid arguments: {str(e)}"

        return await self._execute_command(command, args, bot_state, message)
