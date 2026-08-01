#!/usr/bin/env python3
"""
ResaleBot — CLI tool that monitors Discord and Twitter for limited product drops.
"""

import argparse
import json
import logging
import sys
from threading import Thread
from typing import NoReturn

from colorama import Fore, Style, init as colorama_init

from config import config, load_keywords, save_keywords, setup_logging
from monitor import DiscordBot, TwitterMonitor, keywords_to_patterns

colorama_init(autoreset=True)
log = logging.getLogger("resalebot")


def cmd_monitor(args: argparse.Namespace) -> None:
    keywords = load_keywords()
    if not keywords:
        print(
            f"{Fore.RED}No keywords configured. "
            f"Use 'add-keyword' first or edit keywords.json{Style.RESET_ALL}"
        )
        sys.exit(1)

    patterns = keywords_to_patterns(keywords)

    if not config.use_discord_bot and not config.use_discord_webhook and not config.use_twitter:
        print(
            f"{Fore.YELLOW}Warning: No Discord token, webhook, or Twitter creds set. "
            f"Check .env{Style.RESET_ALL}"
        )

    threads: list[Thread] = []

    if config.use_discord_bot or config.use_discord_webhook:
        db = DiscordBot()
        if args.channels:
            channels = []
            for c in args.channels:
                parts = c.split(":")
                channels.append({
                    "id": parts[0],
                    "name": parts[1] if len(parts) > 1 else parts[0],
                })
            db.set_channels(channels)
        t = Thread(
            target=db.run,
            args=(patterns, config.discord_poll_interval),
            daemon=True,
        )
        t.start()
        threads.append(t)
        print(
            f"{Fore.GREEN} Discord monitor active ({Fore.CYAN}{config.discord_poll_interval}s{Style.RESET_ALL})"
        )

    if config.use_twitter:
        tm = TwitterMonitor()
        t = Thread(
            target=tm.run,
            args=(patterns, keywords, config.poll_interval),
            daemon=True,
        )
        t.start()
        threads.append(t)
        print(
            f"{Fore.GREEN} Twitter monitor active ({Fore.CYAN}{config.poll_interval}s{Style.RESET_ALL})"
        )

    if not threads:
        print(
            f"{Fore.RED}No monitors started. Set at least one source in .env{Style.RESET_ALL}"
        )
        sys.exit(1)

    print(f"\n  Monitoring {len(keywords)} keywords. Press Ctrl+C to stop.\n")
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Shutting down...{Style.RESET_ALL}")


def cmd_add_keyword(args: argparse.Namespace) -> None:
    keywords = load_keywords()
    new = args.keyword.strip()
    if not new:
        print(f"{Fore.RED}Keyword cannot be empty.{Style.RESET_ALL}")
        return
    if new in keywords:
        print(f"{Fore.YELLOW}Keyword already exists: '{new}'{Style.RESET_ALL}")
        return
    keywords.append(new)
    save_keywords(keywords)
    print(f"{Fore.GREEN} Added keyword: '{new}' ({len(keywords)} total){Style.RESET_ALL}")


def cmd_list_keywords(args: argparse.Namespace) -> None:
    keywords = load_keywords()
    if not keywords:
        print(f"{Fore.YELLOW}No keywords configured.{Style.RESET_ALL}")
        return
    print(f"{Fore.CYAN}Keywords ({len(keywords)}):{Style.RESET_ALL}")
    for i, kw in enumerate(keywords, 1):
        print(f"  {i}. {kw}")


def cmd_buy(args: argparse.Namespace) -> None:
    product = args.product or "unknown"
    url = args.url or "N/A"
    print(f"\n  {'='*50}")
    print(f"  {Fore.GREEN}AUTO-BUY STUB{Style.RESET_ALL}")
    print(f"  Would purchase: {Fore.CYAN}{product}{Style.RESET_ALL}")
    print(f"  URL:            {Fore.CYAN}{url}{Style.RESET_ALL}")
    print(f"  Captcha key:    {'configured' if config.captcha_api_key else 'NOT SET'}")
    print(f"  {'='*50}\n")
    print(
        "  Auto-buy is a stub. Implement site-specific "
        "checkout logic in a subclass / plugin."
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="resalebot",
        description="Monitor Discord & Twitter for limited-edition product drops.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  resalebot monitor --channels 12345:general\n"
            "  resalebot add-keyword \"RTX 5090\"\n"
            "  resalebot list-keywords\n"
            "  resalebot buy --product \"Yeezy Slide\" --url https://example.com\n"
        ),
    )

    sub = p.add_subparsers(dest="command", required=True)

    # monitor
    m = sub.add_parser("monitor", help="Start monitoring Discord & Twitter")
    m.add_argument(
        "--channels", nargs="+", default=[],
        help="Discord channel IDs (format: id:name)",
    )
    m.set_defaults(func=cmd_monitor)

    # add-keyword
    a = sub.add_parser("add-keyword", help="Add a keyword to watch")
    a.add_argument("keyword", help="Keyword or regex pattern")
    a.set_defaults(func=cmd_add_keyword)

    # list-keywords
    lk = sub.add_parser("list-keywords", help="Show all watched keywords")
    lk.set_defaults(func=cmd_list_keywords)

    # buy
    b = sub.add_parser("buy", help="Stub auto-buy command")
    b.add_argument("--product", help="Product name")
    b.add_argument("--url", help="Purchase URL")
    b.set_defaults(func=cmd_buy)

    return p


def main() -> NoReturn:
    setup_logging()
    parser = build_parser()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted.{Style.RESET_ALL}")
    except Exception as e:
        log.exception("unhandled error: %s", e)
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()