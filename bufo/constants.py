import os

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSONA_DIR = os.path.join(_BASE_DIR, "persona")
PERSONA_TO_ID_MAPPING_FILE = os.path.join(PERSONA_DIR, "persona_to_id.json")

COMMAND_PREFIX = "$bufo"