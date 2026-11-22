"""Minimal stand-in for the private app's utils/config.py.

The real config module also resolves the database path and creates folders on
import, which this showcase does not need. money_format.py only reads
CURRENCY_SYMBOL, so that is the one value kept here (same value as the app).
"""

CURRENCY_SYMBOL = "Rs"
