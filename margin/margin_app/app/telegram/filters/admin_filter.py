from app.telegram.config import BotConfig  

config = BotConfig()

def is_admin(user_id: int) -> bool:
    """
    Checks if a given user ID is in the list of admin IDs from config.

    Args:
        user_id (int): The Telegram user ID to check.

    Returns:
        bool: True if the user is an admin, False otherwise.
    """
    return user_id in config.ADMINS
