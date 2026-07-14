from __future__ import annotations


def clamp_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words])


def safe_path_id(identifier: str) -> str:
    return identifier.replace(":", "_").replace("/", "_").replace("\\", "_").replace(" ", "_")
