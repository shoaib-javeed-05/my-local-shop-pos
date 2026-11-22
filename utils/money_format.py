from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from utils.config import CURRENCY_SYMBOL


MONEY_INPUT_REGEX = r"^\d*\.?\d*$"
INTEGER_INPUT_REGEX = r"^[0-9]*$"
SIGNED_INTEGER_INPUT_REGEX = r"^-?[0-9]*$"
TWOPLACES = Decimal("0.01")


def to_decimal(value, default=Decimal("0.00")) -> Decimal:
    try:
        if value is None or str(value).strip() == "":
            return default
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return default


def money(value) -> Decimal:
    return to_decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def format_money(value) -> str:
    return f"{CURRENCY_SYMBOL}{money(value):.2f}"


def format_percent(value) -> str:
    amount = to_decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    if amount == 0:
        return "0%"
    text = format(amount, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return f"{text}%"


def format_currency(value) -> str:
    return format_money(value)


def format_percentage(value) -> str:
    return format_percent(value)


def format_number_input(value, force_decimals: bool = False) -> str:
    amount = to_decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    text = format(amount, "f")
    if not force_decimals and "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def format_discount_value(discount_type: str, discount_value, zero_label: str = "No Discount") -> str:
    value = to_decimal(discount_value)
    if value <= 0:
        return zero_label
    if discount_type == "fixed":
        return format_money(value)
    return format_percent(value)


def sanitize_money_input(value) -> str:
    text = "" if value is None else str(value).strip()
    if not text:
        return ""
    lower_text = text.lower()
    if "e" in lower_text:
        text = text[:lower_text.index("e")]

    cleaned = []
    dot_seen = False
    for char in text:
        if char.isdigit():
            cleaned.append(char)
        elif char == "." and not dot_seen:
            cleaned.append(char)
            dot_seen = True

    text = "".join(cleaned)
    if not text:
        return ""
    if text.startswith("."):
        text = f"0{text}"

    if "." in text:
        whole, cents = text.split(".", 1)
        whole = whole.lstrip("0") or "0"
        return f"{whole}.{cents[:2]}"

    return text.lstrip("0") or "0"


def sanitize_integer_input(value, allow_negative: bool = False) -> str:
    text = "" if value is None else str(value).strip()
    if not text:
        return ""

    is_negative = allow_negative and text.startswith("-")
    if "." in text:
        text = text.split(".", 1)[0]
    digits = "".join(char for char in text if char.isdigit())
    if not digits:
        return "-" if is_negative else ""

    digits = digits.lstrip("0") or "0"
    if is_negative and digits != "0":
        return f"-{digits}"
    return digits
