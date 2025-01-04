import os
from copy import deepcopy
from discord import Message

from bufo.constants import PERSONA_DIR
from bufo.utils.logging_utils import get_logger

logger = get_logger(__name__)


def get_or_create_user_log_file(user_id: int, user_name: str) -> str:
    """
    Returns path to user log file, creating it if it doesn't exist
    """
    log_file = os.path.join(PERSONA_DIR, str(user_id), "msg_log.txt")
    if not os.path.exists(log_file):
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)
        open(log_file, "w").close()
        # create a file with username for easy ID
        open(os.path.join(log_dir, f'_{user_name}.txt'), "w").close()

    return log_file


def log_user_msg_to_file(message: Message) -> None:
    """
    Logs message to user file
    """
    user_id = message.author.id
    user_name = message.author.name
    log_file = get_or_create_user_log_file(user_id, user_name)
    with open(log_file, "a") as f:
        if sanitized_msg := sanitize(message.content):
            f.write(f"{sanitized_msg}\n")


"""STRING PROCESSING UTILS"""
import re


def sanitize(message: str) -> str:
    orig = deepcopy(message)

    # Remove user mentions (<@123456789>)
    message = re.sub(r'<@\d+>', '', message)

    # Remove links except for whitelisted domains
    url_whitelist = ['tenor.com']
    safe_domains = [re.escape(domain) for domain in url_whitelist]
    whitelist_pattern = '|'.join(safe_domains)
    message = re.sub(f'https?://(?!(?:{whitelist_pattern})\S+)\S+', '',
                     message)  # negative lookahead

    # Remove extra whitespace
    message = ' '.join(message.split())

    # Remove zero-width spaces and other invisible characters
    message = re.sub(r'[\u200B-\u200D\uFEFF]', '', message)

    # Remove control characters except newlines
    message = re.sub(r'[\x00-\x08\x0B-\x1F\x7F]', '', message)

    message = message.strip()

    if message != orig:
        logger.info(f"Sanitized message: {orig} -> {message}")

    return message
