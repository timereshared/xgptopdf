"""Utility functions for xgptopdf."""


import sys


print_info_messages = False


def error(message):
    """Error detected. Print the message and exit."""
    print(message, file=sys.stderr)
    sys.exit(1)


def warn(message):
    """Print a warning."""
    print(message, file=sys.stderr)


def info(message):
    """Print an informational message, if enabled."""
    if print_info_messages:
        print(message, file=sys.stderr)


def split_18(word):
    """Split a 36 bit word into two 18 bit quantities."""
    return word >> 18, word & 0x3FFFF


def split_9(word):
    """Split a 36 bit word into four 9 bit quantities."""
    mask = 0b111111111
    return word >> 27, word >> 18 & mask, word >> 9 & mask, word & mask


def split_7(word):
    """Convert a 36 bit word into 7 5 bit values, discarding the last bit."""
    val_35 = word >> 1
    chars = []
    for i in range(4, -1, -1):
        chars.append((val_35 >> (i * 7)) & 0x7F)
    return chars


# SAIL Character Map (7-bit values 0-127)
# Null (0) is not converted.
SAIL_MAP = [
    "", "↓", "α", "β", "∧", "¬", "ε", "π",
    "λ", "\t", "\n", "\v", "\f", "\r", "∞", "∂",
    "⊂", "⊃", "∩", "∪", "∀", "∃", "⊗", "↔",
    "_", "→", "~", "≠", "≤", "≥", "≡", "∨",
    " ", "!", '"', "#", "$", "%", "&", "'",
    "(", ")", "*", "+", ",", "-", ".", "/",
    "0", "1", "2", "3", "4", "5", "6", "7",
    "8", "9", ":", ";", "<", "=", ">", "?",
    "@", "A", "B", "C", "D", "E", "F", "G",
    "H", "I", "J", "K", "L", "M", "N", "O",
    "P", "Q", "R", "S", "T", "U", "V", "W",
    "X", "Y", "Z", "[", "\\", "]", "↑", "←",
    "`", "a", "b", "c", "d", "e", "f", "g",
    "h", "i", "j", "k", "l", "m", "n", "o",
    "p", "q", "r", "s", "t", "u", "v", "w",
    "x", "y", "z", "{", "|", "⎇", "}", "\b"
]


def sail_ascii_to_utf8(char_code):
    """Convert an individual character code in SAIL ASCII to UTF-8."""
    return SAIL_MAP[char_code]


def sail_ascii_bytes_to_utf8(buf):
    """Convert a list of bytes  in SAIL ASCII to a UTF-8 string."""
    return "".join([sail_ascii_to_utf8(ch) for ch in buf])


def packed_sail_ascii_to_utf8(words):
    """Convert a list of 36 bit words representing a string of
    Stanford AI Lab ASCII chracters into a UTF-8 string."""
    chars = []
    for word in words:
        for char_code in split_7(word):
            chars.append(sail_ascii_to_utf8(char_code))
    return "".join(chars)
