from decimal import Decimal

import pytest

from utils.money_format import (
    format_discount_value,
    format_money,
    format_number_input,
    format_percent,
    money,
    sanitize_integer_input,
    sanitize_money_input,
    to_decimal,
)


# --- to_decimal -------------------------------------------------------------

@pytest.mark.parametrize("value", [None, "", "   "])
def test_to_decimal_blank_values_use_default(value):
    assert to_decimal(value) == Decimal("0.00")


def test_to_decimal_invalid_text_uses_default():
    assert to_decimal("abc") == Decimal("0.00")
    assert to_decimal("abc", default=Decimal("-1")) == Decimal("-1")


def test_to_decimal_parses_numbers_and_strips_spaces():
    assert to_decimal(" 12.50 ") == Decimal("12.50")
    assert to_decimal(7) == Decimal("7")


def test_to_decimal_goes_through_str_so_floats_keep_their_printed_value():
    # Decimal(0.1) would be 0.1000000000000000055...; the module avoids that.
    assert to_decimal(0.1) == Decimal("0.1")


# --- money (2 places, half-up) ----------------------------------------------

@pytest.mark.parametrize(
    "value, expected",
    [
        ("2.675", Decimal("2.68")),   # half-up, not banker's rounding
        (2.675, Decimal("2.68")),     # float input rounds the same way
        ("0.005", Decimal("0.01")),
        ("0.004", Decimal("0.00")),
        ("-1.005", Decimal("-1.01")),  # half-up rounds away from zero
        ("1650", Decimal("1650.00")),
        (None, Decimal("0.00")),
    ],
)
def test_money_rounds_half_up_to_two_places(value, expected):
    assert money(value) == expected


def test_line_totals_add_up_exactly():
    # 3 x 0.10 is 0.30000000000000004 in float arithmetic.
    assert money(sum(money("0.10") for _ in range(3))) == Decimal("0.30")


# --- display formatting -----------------------------------------------------

def test_format_money_uses_currency_symbol_and_two_decimals():
    assert format_money(1650) == "Rs1650.00"
    assert format_money("99.999") == "Rs100.00"
    assert format_money("") == "Rs0.00"


@pytest.mark.parametrize(
    "value, expected",
    [(0, "0%"), ("10", "10%"), ("12.50", "12.5%"), ("7.25", "7.25%"), ("33.333", "33.33%")],
)
def test_format_percent_drops_trailing_zeros(value, expected):
    assert format_percent(value) == expected


@pytest.mark.parametrize(
    "value, force, expected",
    [("12.50", False, "12.5"), ("12.50", True, "12.50"), ("3", False, "3"), ("abc", False, "0")],
)
def test_format_number_input(value, force, expected):
    assert format_number_input(value, force_decimals=force) == expected


# --- discount labels --------------------------------------------------------

def test_fixed_discount_is_shown_as_money():
    assert format_discount_value("fixed", 50) == "Rs50.00"


def test_percentage_discount_is_shown_as_percent():
    assert format_discount_value("percentage", "12.5") == "12.5%"


@pytest.mark.parametrize("value", [0, "0", -5, None, ""])
def test_zero_or_negative_discount_uses_zero_label(value):
    assert format_discount_value("fixed", value) == "No Discount"
    assert format_discount_value("percentage", value, zero_label="-") == "-"


# --- input sanitising (cash, price and quantity fields) ---------------------

@pytest.mark.parametrize(
    "raw, expected",
    [
        (None, ""),
        ("", ""),
        ("abc", ""),
        ("1650", "1650"),
        ("00012.345", "12.34"),   # leading zeros removed, cut to 2 decimals
        (".5", "0.5"),
        ("1.2.3", "1.23"),        # only the first dot is kept
        ("12.", "12."),           # a trailing dot is kept while typing
        ("Rs 1,500", "1500"),     # symbols and separators dropped
        ("1e5", "1"),             # exponent notation is not accepted
        ("-20", "20"),            # money input is never negative
        ("000", "0"),
    ],
)
def test_sanitize_money_input(raw, expected):
    assert sanitize_money_input(raw) == expected


@pytest.mark.parametrize(
    "raw, allow_negative, expected",
    [
        (None, False, ""),
        ("007", False, "7"),
        ("12.9", False, "12"),    # decimals are cut, not rounded
        ("-5", False, "5"),
        ("-5", True, "-5"),
        ("-", True, "-"),         # lets the user start typing a negative number
        ("-0", True, "0"),
        ("x", False, ""),
    ],
)
def test_sanitize_integer_input(raw, allow_negative, expected):
    assert sanitize_integer_input(raw, allow_negative=allow_negative) == expected
