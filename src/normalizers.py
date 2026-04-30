Сюда кладём нормализацию ФИО, Telegram, телефона, email, названий колонок и событий.
import re
import unicodedata
import pandas as pd


EMPTY_TOKENS = {
    "",
    "-",
    "—",
    "нет",
    "не знаю",
    "не указано",
    "не указан",
    "nan",
    "none",
    "null",
    "0",
}


def normalize_text_base(value) -> str | None:
    """
    Basic text normalization: unicode normalization, trimming and empty handling.
    """
    if pd.isna(value):
        return None

    value = str(value)
    value = unicodedata.normalize("NFC", value)
    value = value.replace("\u00a0", " ")
    value = value.strip()

    if value == "":
        return None

    return value


def clean_raw_value(value) -> str | None:
    """
    Clean raw cell value and convert obvious empty tokens to None.
    """
    value = normalize_text_base(value)

    if value is None:
        return None

    value_lower = value.lower().strip()

    if value_lower in EMPTY_TOKENS:
        return None

    return value


def normalize_colname(column: str) -> str:
    """
    Normalize a column name for pattern matching.
    """
    column = str(column)
    column = unicodedata.normalize("NFC", column)
    column = column.strip().lower().replace("ё", "е")
    column = re.sub(r"\s+", " ", column)

    return column


def normalize_event_name_for_match(value: str) -> str:
    """
    Normalize event name for alias matching.
    """
    value = normalize_text_base(value)

    if value is None:
        return ""

    value = value.lower().replace("ё", "е")
    value = re.sub(r"\s+", " ", value)

    return value


def norm_fio(value) -> str | None:
    """
    Normalize full name.
    """
    value = clean_raw_value(value)

    if value is None:
        return None

    value = unicodedata.normalize("NFC", value)
    value = value.lower().replace("ё", "е")
    value = re.sub(r"[^a-zа-я\s-]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    if len(value) < 2:
        return None

    return value


def fio_signature(value) -> str | None:
    """
    Stable FIO signature.

    It makes 'Иванов Иван' and 'Иван Иванов' equivalent by sorting tokens.
    This is useful for conflict checks and fallback identity keys.
    """
    fio = norm_fio(value)

    if fio is None:
        return None

    tokens = fio.split()
    tokens = [token for token in tokens if len(token) > 1]

    if not tokens:
        return None

    return " ".join(sorted(tokens))


def norm_telegram(value) -> str | None:
    """
    Normalize Telegram username.
    """
    value = clean_raw_value(value)

    if value is None:
        return None

    value = unicodedata.normalize("NFC", value)
    value = value.lower().strip()

    value = value.replace("https://", "").replace("http://", "")
    value = value.replace("t.me/", "")
    value = value.replace("telegram.me/", "")
    value = value.replace("@", "")
    value = value.strip()

    value = re.sub(r"[^a-z0-9_]", "", value)

    # Telegram usernames are usually at least 5 characters.
    # Shorter strings are often noise.
    if len(value) < 5:
        return None

    if value in EMPTY_TOKENS:
        return None

    return value


def norm_phone(value) -> str | None:
    """
    Normalize Russian phone number to 11-digit format starting with 7.
    """
    value = clean_raw_value(value)

    if value is None:
        return None

    digits = re.sub(r"\D", "", value)

    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]

    if len(digits) == 10:
        digits = "7" + digits

    if len(digits) == 11 and digits.startswith("7"):
        return digits

    return None


def norm_email(value) -> str | None:
    """
    Normalize email.
    """
    value = clean_raw_value(value)

    if value is None:
        return None

    value = value.lower().strip()
    value = re.sub(r"\s+", "", value)

    if re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value):
        return value

    return None


def norm_simple_category(value) -> str | None:
    """
    Normalize simple categorical fields such as group, program or course.
    """
    value = clean_raw_value(value)

    if value is None:
        return None

    value = unicodedata.normalize("NFC", value)
    value = value.lower().replace("ё", "е")
    value = re.sub(r"\s+", " ", value).strip()

    return value or None

