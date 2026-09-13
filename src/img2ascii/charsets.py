"""Shared character sets for ASCII art conversion.

All sets are ordered darkest -> lightest (index 0 = darkest pixel).
"""

CHARSETS = {
    "default": "@%#*+=-:. ",
    "detailed": "@#%+=:-$ ",
    "ramp": "%@#*+o:. ",
    "fine": "@#W$%&*+=;:~-,. ",
    "binary": "# ",
    "blocks": "\u2593\u2592\u2591 ",  # ▓ ▒ ░
}
