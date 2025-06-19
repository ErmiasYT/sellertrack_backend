from loguru import logger
import sys

# Configure loguru
logger.remove()  # Remove default
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>", level="INFO")

# Example usage across app:
# from utils.logger import logger
# logger.info("Something happened")
# logger.error("Uh oh")

# Optional: file logging
# logger.add("logs/runtime.log", rotation="1 day")