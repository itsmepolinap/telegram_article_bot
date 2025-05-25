import re


def check_url_format(text: str) -> bool:
    """
    Простейшая валидация URL.
    """
    pattern = re.compile(r"^https?://[^\s]+$")
    return bool(pattern.match(text))
