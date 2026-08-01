import os
import re
import json
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def str_to_bool(v: str) -> bool:
    return v.strip().lower() in ("1", "true", "yes", "y")


class Config:
    discord_bot_token: Optional[str] = None
    discord_webhook_url: Optional[str] = None
    twitter_bearer_token: Optional[str] = None
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_secret: Optional[str] = None
    captcha_api_key: Optional[str] = None
    webhook_url: Optional[str] = None
    poll_interval: int = 30
    discord_poll_interval: int = 15
    twitter_keywords_file: str = "keywords.json"
    log_file: str = "monitor.log"
    log_level: str = "INFO"
    notify_command: str = ""

    def __init__(self) -> None:
        self.discord_bot_token = os.getenv("DISCORD_BOT_TOKEN")
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.twitter_api_key = os.getenv("TWITTER_API_KEY")
        self.twitter_api_secret = os.getenv("TWITTER_API_SECRET")
        self.twitter_access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.twitter_access_secret = os.getenv("TWITTER_ACCESS_SECRET")
        self.captcha_api_key = os.getenv("CAPTCHA_API_KEY")
        self.webhook_url = os.getenv("WEBHOOK_URL")

        raw_interval = os.getenv("POLL_INTERVAL", "30")
        try:
            self.poll_interval = int(raw_interval)
        except ValueError:
            self.poll_interval = 30

        raw_disc_interval = os.getenv("DISCORD_POLL_INTERVAL", "15")
        try:
            self.discord_poll_interval = int(raw_disc_interval)
        except ValueError:
            self.discord_poll_interval = 15

        self.twitter_keywords_file = os.getenv("KEYWORDS_FILE", "keywords.json")
        self.log_file = os.getenv("LOG_FILE", "monitor.log")
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.notify_command = os.getenv("NOTIFY_COMMAND", "")

    @property
    def use_discord_bot(self) -> bool:
        return bool(self.discord_bot_token)

    @property
    def use_discord_webhook(self) -> bool:
        return bool(self.discord_webhook_url)

    @property
    def use_twitter(self) -> bool:
        return bool(self.twitter_bearer_token and self.twitter_api_key)


config = Config()


def load_keywords(path: Optional[str] = None) -> list[str]:
    p = path or config.twitter_keywords_file
    if os.path.exists(p):
        with open(p) as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    return []


def save_keywords(keywords: list[str], path: Optional[str] = None) -> None:
    p = path or config.twitter_keywords_file
    with open(p, "w") as f:
        json.dump(keywords, f, indent=2)


def setup_logging() -> None:
    level = getattr(logging, config.log_level, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(config.log_file),
            logging.StreamHandler(),
        ],
    )