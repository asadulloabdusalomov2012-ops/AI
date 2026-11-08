import os
import sys
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from openai import OpenAI

# ---------------------------------------------------------------------------
# CONFIGURATION & LOGGING SETUP
# ---------------------------------------------------------------------------

# Configure console logging so events are cleanly visible during video recording and in Railway logs
logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# OpenRouter model — easy to swap for another free-tier model later
MODEL_NAME = "nvidia/nemotron-3-ultra-550b-a55b:free"

# Path to the editable system prompt file (edit this file, not this script,
# to change what the AI talks about / how it behaves)
SYSTEM_PROMPT_FILE = "system_prompt.txt"

# Read Environment Variables directly from the OS (no .env file, no python-dotenv)
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
PHONE_NUMBER = os.environ.get("PHONE_NUMBER")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# Optional: TELEGRAM_SESSION string environment variable for headless hosting (Railway)
SESSION_STRING = os.environ.get("TELEGRAM_SESSION", "")

# Validate required configuration before doing anything else
if not all([API_ID, API_HASH, OPENROUTER_API_KEY]):
    logger.error("Missing environment variables! Please set API_ID, API_HASH, and OPENROUTER_API_KEY.")
    sys.exit(1)

# Convert API_ID to integer for Telethon
try:
    API_ID = int(API_ID)
except ValueError:
    logger.error("API_ID must be a valid integer.")
    sys.exit(1)


def load_system_prompt() -> str:
    """Loads the AI's instructions from system_prompt.txt.
    Edit that file any time to change the AI's behavior — no code changes needed.
    """
    try:
        with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                return content
    except FileNotFoundError:
        logger.warning(f"{SYSTEM_PROMPT_FILE} not found, using a default fallback prompt.")

    return "You are a helpful AI assistant replying on behalf of the account owner via Telegram. Keep answers friendly and concise."


SYSTEM_PROMPT = load_system_prompt()

# ---------------------------------------------------------------------------
# CLIENT INITIALIZATION
# ---------------------------------------------------------------------------

# Initialize OpenAI-compatible client pointed at OpenRouter's API base URL
ai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Initialize Telethon Client:
# If TELEGRAM_SESSION env var exists, load from memory (StringSession) — used on Railway.
# Otherwise, default to saving locally in 'userbot_session.session' — used for local runs.
if SESSION_STRING:
    logger.info("Initializing Telethon using StringSession from environment variables...")
    telegram_client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    logger.info("Initializing Telethon using local SQLite file session...")
    telegram_client = TelegramClient("userbot_session", API_ID, API_HASH)

# ---------------------------------------------------------------------------
# EVENT HANDLERS
# ---------------------------------------------------------------------------

@telegram_client.on(events.NewMessage(incoming=True))
async def handle_new_message(event):
    """Listens for incoming private messages and replies using an OpenRouter AI model."""

    # Requirement: Strictly process private DMs only (skip groups and channels)
    if not event.is_private:
        return

    # Skip messages sent by yourself (outgoing DMs, Saved Messages, etc.)
    # Without this check, the bot could end up replying to its own messages.
    if event.out:
        return

    user_text = event.raw_text
    if not user_text:
        # Ignore non-text messages (stickers, photos without caption, etc.)
        return

    sender = await event.get_sender()
    sender_name = getattr(sender, "first_name", "Unknown User")

    # Log incoming message to console
    logger.info(f"📥 [Incoming DM] From: {sender_name} (ID: {event.sender_id}) | Message: '{user_text}'")

    # Call OpenRouter API with basic error handling
    try:
        response = ai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=500
        )

        ai_reply = response.choices[0].message.content.strip()
        logger.info(f"🤖 [AI Generated Reply]: '{ai_reply}'")

        # Send the AI response back to the sender
        await event.reply(ai_reply)
        logger.info(f"📤 [Outgoing DM] Sent reply to {sender_name}")

    except Exception as e:
        logger.error(f"❌ Error communicating with OpenRouter or sending message: {e}")

# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

def main():
    logger.info("Starting Telegram Userbot...")

    # Start Telethon client (prompts for phone and SMS code on first interactive terminal run)
    telegram_client.start(phone=PHONE_NUMBER)

    # NOTE: local file sessions can't be converted to a string session automatically.
    # To get a TELEGRAM_SESSION string for Railway, run generate_session.py once
    # (see the separate script) and copy its output into Railway's Variables tab.

    logger.info(f"Userbot is live! Using model: '{MODEL_NAME}'. Press Ctrl+C to stop.")

    # Keep running and listening for events
    telegram_client.run_until_disconnected()


if __name__ == "__main__":
    main()
