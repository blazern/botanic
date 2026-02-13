from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

_ARTICLE_RE = re.compile(r"^(?:[1-9]\d{0,2})$")  # 1..999

@dataclass
class Article:
    url: str
    text: str

def get_article_text(number: str, base_dir: Path) -> Article:
    """
    Return article markdown text for `number` from `base_dir/{number}.md`.
    """
    if not _ARTICLE_RE.match(number):
        raise ValueError(f"Invalid article number: {number}")

    base = Path(base_dir).resolve()
    if not base.exists() or not base.is_dir():
        raise RuntimeError(f"Articles dir is invalid or missing: {base}")

    candidate = (base / f"{number}.md").resolve()

    # Prevent path traversal / symlink escapes
    # e.g. /app/data/illness_schedule/../../../../etc/passwd.md
    try:
        candidate.relative_to(base)
    except ValueError as e:
        raise RuntimeError("Invalid article path (escape attempt)") from e

    if not candidate.exists() or not candidate.is_file():
        raise FileNotFoundError(f"Article not found: {number}")

    file_text = candidate.read_text(encoding="utf-8")
    url, _, text = file_text.partition("\n")
    return Article(url, text)
