import os
import json
import random
from discord import Message

from bufo.constants import PERSONA_DIR, PERSONA_TO_ID_MAPPING_FILE
from bufo.handlers.base import AbstractHandler
from bufo.utils import get_logger

from typing import Any, Optional

logger = get_logger(__name__)


class UserMessageHandler(AbstractHandler):
    """Handles non-command messages"""

    def __init__(self, cfg: Any):
        super().__init__(cfg)

    async def handle(self, bot_state: 'BufoBot',
                     message: Message) -> Optional[str]:
        """
        Handle non-command messages
        
        Args:
            message: Discord message object
            
        Returns:
            Optional response string
        """
        if not bot_state.cfg.enable_responses:
            logger.info("Responses disabled")
            return None

        # with 40% probability, respond to messages
        if random.random() < 0.6:
            logger.info("Unlucky, bud.")
            return None

        with open(PERSONA_TO_ID_MAPPING_FILE) as f:
            persona_to_id = json.load(f)

        user_id = persona_to_id.get(bot_state.cfg.persona)

        if not user_id:
            return None

        response_file = os.path.join(PERSONA_DIR, user_id, "msg_log.txt")

        with open(response_file) as f:
            responses = f.readlines()

        if responses:
            response = random.choice(responses).strip()
            return response
