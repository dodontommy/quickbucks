import re
from typing import Optional


SNEAKER_KEYWORDS = [
    "sneaker", "yeezy", "jordan", "nike", "adidas", "air force", "dunk",
    "off-white", "travis scott", "supreme", "hype", "drop", "restock",
]
GPU_KEYWORDS = [
    "rtx", "geforce", "radeon", "gpu", "graphics card", "3080", "3090",
    "4070", "4080", "4090", "5090", "5080", "7900", "7800",
]
TICKET_KEYWORDS = [
    "ticket", "concert", "festival", "lollapalooza", "coachella",
    "glastonbury", "rolling loud", "presale", "box office",
]


def detect_product_type(text: str) -> str:
    lower = text.lower()
    sneaker_score = sum(1 for kw in SNEAKER_KEYWORDS if kw in lower)
    gpu_score = sum(1 for kw in GPU_KEYWORDS if kw in lower)
    ticket_score = sum(1 for kw in TICKET_KEYWORDS if kw in lower)

    if gpu_score > sneaker_score and gpu_score >= ticket_score:
        return "gpu"
    if ticket_score > sneaker_score and ticket_score > gpu_score:
        return "ticket"
    if sneaker_score > 0:
        return "sneaker"
    return "other"


URL_PATTERN = re.compile(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+")


def extract_url(text: str) -> Optional[str]:
    match = URL_PATTERN.search(text)
    return match.group(0) if match else None


PRICE_PATTERNS = [
    re.compile(r"\$\s?(\d{1,6}(?:,\d{3})*(?:\.\d{2})?)"),
    re.compile(r"(\d{1,6}(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|usd|dollars)"),
]


def extract_price(text: str) -> Optional[float]:
    for pat in PRICE_PATTERNS:
        match = pat.search(text)
        if match:
            raw = match.group(1).replace(",", "")
            try:
                return float(raw)
            except ValueError:
                continue
    return None