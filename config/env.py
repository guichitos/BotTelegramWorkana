"""Environment loader using python-dotenv."""
from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
BOT_ENV = os.getenv("BOT_ENV", "dev").lower()

ENV_FILES = {
    "dev": ".env.dev",
    "prod": ".env.prod",
}

env_file = ENV_FILES.get(BOT_ENV, ENV_FILES["dev"])
load_dotenv(BASE_DIR / env_file)
