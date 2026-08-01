import json
import logging
import re
import time
import subprocess
from typing import Optional
from threading import Thread, Event

import requests

from config import config, load_keywords
from detectors import detect_product_type, extract_url, extract_price

log = logging.getLogger("monitor")


class Alert:
    def __init__(self, source: str, channel: str, author: str, text: str, keyword: str) -> None:
        self.source = source
        self.channel = channel
        self.author = author
        self.text = text
        self.keyword = keyword
        self.product_type = detect_product_type(text)
        self.url = extract_url(text)
        self.price = extract_price(text)

    def summary(self) -> str:
        parts = [
            f"[{self.source}]",
            f"#{self.channel}",
            f"@{self.author}",
            f"matched '{self.keyword}'",
        ]
        if self.url:
            parts.append(f"url={self.url}")
        if self.price is not None:
            parts.append(f"${self.price:.2f}")
        parts.append(f"type={self.product_type}")
        return " ".join(parts)


def keywords_to_patterns(keywords: list[str]) -> list[re.Pattern]:
    compiled = []
    for kw in keywords:
        try:
            compiled.append(re.compile(re.escape(kw), re.IGNORECASE))
        except re.error:
            compiled.append(re.compile(re.escape(kw), re.IGNORECASE))
    return compiled


def match_keywords(text: str, patterns: list[re.Pattern]) -> list[str]:
    matched = []
    for pat in patterns:
        if pat.search(text):
            matched.append(pat.pattern)
    return matched


def send_desktop_notification(title: str, body: str) -> None:
    if config.notify_command:
        try:
            subprocess.Popen(
                config.notify_command.format(title=title, body=body),
                shell=True,
            )
        except Exception as e:
            log.warning("notify command failed: %s", e)
    else:
        try:
            subprocess.Popen(
                ["notify-send", title, body],
            )
        except FileNotFoundError:
            pass


def send_webhook(text: str) -> None:
    url = config.webhook_url
    if not url:
        return
    try:
        requests.post(url, json={"content": text}, timeout=10)
    except requests.RequestException as e:
        log.warning("webhook post failed: %s", e)


class DiscordBot:
    def __init__(self) -> None:
        self.token = config.discord_bot_token
        self.webhook_url = config.discord_webhook_url
        self.channels: list[dict] = []
        self._stop = Event()
        self._last_ids: dict[str, Optional[str]] = {}

    def set_channels(self, channels: list[dict]) -> None:
        self.channels = channels

    def poll_once(self, patterns: list[re.Pattern]) -> list[Alert]:
        alerts: list[Alert] = []
        alerts.extend(self._poll_discord_api(patterns))
        alerts.extend(self._poll_webhook(patterns))
        return alerts

    def _poll_discord_api(self, patterns: list[re.Pattern]) -> list[Alert]:
        if not self.token:
            return []
        headers = {"Authorization": f"Bot {self.token}"}
        alerts: list[Alert] = []

        for ch in self.channels:
            channel_id = ch.get("id", ch.get("channel_id"))
            guild_id = ch.get("guild_id")
            if not channel_id:
                continue
            try:
                params: dict = {"limit": 5}
                last_id = self._last_ids.get(str(channel_id))
                if last_id:
                    params["after"] = last_id

                resp = requests.get(
                    f"https://discord.com/api/v10/channels/{channel_id}/messages",
                    headers=headers,
                    params=params,
                    timeout=15,
                )
                if resp.status_code == 429:
                    log.warning("rate limited on channel %s", channel_id)
                    time.sleep(5)
                    continue
                if resp.status_code != 200:
                    continue

                messages = resp.json()
                for msg in messages:
                    mid = msg["id"]
                    last = self._last_ids.get(str(channel_id))
                    if last is None or mid > last:
                        self._last_ids[str(channel_id)] = mid

                    matched = match_keywords(msg.get("content", ""), patterns)
                    if matched:
                        for kw in matched:
                            alerts.append(Alert(
                                source="discord",
                                channel=ch.get("name", channel_id),
                                author=msg.get("author", {}).get("username", "?"),
                                text=msg.get("content", ""),
                                keyword=kw,
                            ))

                if not last_id and messages:
                    self._last_ids[str(channel_id)] = messages[0]["id"]

            except requests.RequestException as e:
                log.warning("discord api error on channel %s: %s", channel_id, e)

        return alerts

    def _poll_webhook(self, patterns: list[re.Pattern]) -> list[Alert]:
        if not self.webhook_url:
            return []
        alerts: list[Alert] = []
        try:
            resp = requests.get(
                self.webhook_url.replace("/slack", ""),
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("content", "")
                matched = match_keywords(content, patterns)
                if matched:
                    for kw in matched:
                        alerts.append(Alert(
                            source="discord-webhook",
                            channel="webhook",
                            author=data.get("author", {}).get("username", "?"),
                            text=content,
                            keyword=kw,
                        ))
        except requests.RequestException as e:
            log.warning("webhook poll error: %s", e)
        return alerts

    def run(self, patterns: list[re.Pattern], interval: int) -> None:
        log.info("discord monitor started (interval=%ds)", interval)
        while not self._stop.is_set():
            alerts = self.poll_once(patterns)
            for a in alerts:
                handle_alert(a)
            self._stop.wait(interval)

    def stop(self) -> None:
        self._stop.set()


class TwitterMonitor:
    def __init__(self) -> None:
        self.bearer_token = config.twitter_bearer_token
        self._stop = Event()

    def _search_recent(self, keywords: list[str]) -> list[dict]:
        if not self.bearer_token or not keywords:
            return []
        query = " OR ".join(f'"{kw}"' for kw in keywords)
        try:
            resp = requests.get(
                "https://api.twitter.com/2/tweets/search/recent",
                headers={"Authorization": f"Bearer {self.bearer_token}"},
                params={
                    "query": f"({query}) -is:retweet lang:en",
                    "max_results": 10,
                    "tweet.fields": "author_id,created_at",
                },
                timeout=15,
            )
            if resp.status_code == 429:
                log.warning("twitter rate limited")
                return []
            if resp.status_code != 200:
                log.warning("twitter api error: %s", resp.text)
                return []
            return resp.json().get("data", [])
        except requests.RequestException as e:
            log.warning("twitter request failed: %s", e)
            return []

    def run(self, patterns: list[re.Pattern], keywords: list[str], interval: int) -> None:
        log.info("twitter monitor started (interval=%ds)", interval)
        seen: set[str] = set()
        while not self._stop.is_set():
            tweets = self._search_recent(keywords)
            for tweet in tweets:
                tid = tweet["id"]
                if tid in seen:
                    continue
                seen.add(tid)
                text = tweet.get("text", "")
                matched = match_keywords(text, patterns)
                if matched:
                    for kw in matched:
                        handle_alert(Alert(
                            source="twitter",
                            channel="search/recent",
                            author=tweet.get("author_id", "?"),
                            text=text,
                            keyword=kw,
                        ))
            self._stop.wait(interval)

    def stop(self) -> None:
        self._stop.set()


def handle_alert(alert: Alert) -> None:
    summary = alert.summary()
    log.info("ALERT: %s", summary)
    print(f"\n  {summary}")
    send_desktop_notification(
        f"ResaleBot — {alert.product_type.upper()} detected",
        summary,
    )
    if alert.url:
        send_webhook(f"**{alert.product_type}** | {alert.url} | {alert.text[:200]}")