# 1. Standard library
import logging

# 2. Third-party libraries

# 3. Local application/library imports

def setup_logging():
    # Set up a general logger
    logger = logging.getLogger('bot_pompa')
    logger.setLevel(logging.DEBUG)

    # --- Formatter ---
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')

    # File handler for logs
    file_handler = logging.FileHandler('bot_pompa.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console handler for logs
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    # --- Discord Logger ---
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.DEBUG)  # Overall level: allow DEBUG !!!

    discord_file_handler = logging.FileHandler('bot_pompa.log', encoding='utf-8')
    discord_file_handler.setLevel(logging.WARNING)
    discord_file_handler.setFormatter(formatter)

    discord_console_handler = logging.StreamHandler()
    discord_console_handler.setLevel(logging.DEBUG)
    discord_console_handler.setFormatter(formatter)

    if not discord_logger.handlers:
        discord_logger.addHandler(discord_file_handler)
        discord_logger.addHandler(discord_console_handler)

    # --- ASYNCIO Logger ---
    logging.getLogger('asyncio').setLevel(logging.WARNING)