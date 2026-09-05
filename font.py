"""The Font class represents a SAIL bitmap font."""


# pylint: disable=too-many-instance-attributes


import re
import os

from glyph import Glyph
from utils import split_18, packed_sail_ascii_to_utf8, error, warn


# Override where to get fonts from
font_dir = None


def get_font_dir():
    """Get the directory where fonts are stored."""
    if font_dir:
        return font_dir + "/"
    return os.path.dirname(os.path.abspath(__file__)) + "/fonts/final/"


def get_fallback_font(font_path):
    """If a font can't be found, substitute a fallback font."""
    # This is specified in th1 1977 SPOOL manual
    fallback = f"{font_path}XGP/SYS/GACS25.FNT"
    if not os.path.exists(fallback):
        # If using 1974 fonts
        fallback = f"{font_path}XGP/SYS/FIX20.FNT"
    if not os.path.exists(fallback):
        error(f"Fallback font {fallback} not found.")
    return fallback


def build_font_file_name(font_path, data):
    """Create a filename from path and file components."""
    name = font_path
    name += data['prj'] or "XGP"
    name += "/"
    name += data['prg'] or "SYS"
    name += "/"
    name += data['file']
    name += "."
    name += data['ext'] or "FNT"
    return name


def find_font(name):
    """Find the filename for the given font name."""
    font_path = get_font_dir()
    # If the user supplied a unix file name, and it exists, use it
    if name.find('/') > 0 and os.path.exists(name):
        return name
    # Try building a filename from font name, and if given
    # prj, prg and ext
    pattern = re.compile(r"""
    (?P<file>[^.\[]+)
    (?:\.(?P<ext>[^.\[]+))
    ?(?:\[(?P<prj>[^,]+),(?P<prg>[^\]]+)\])?$
    """, re.VERBOSE)
    match = re.match(pattern, name)
    if match:
        data = match.groupdict()
        full_match = build_font_file_name(font_path, data)
        if os.path.exists(full_match):
            return full_match
        # Try in system dir, eg doc specified ABC.FNT[1,XYZ] then
        # try ABC.FNT[XGP,SYS]
        data['prj'] = "XGP"
        data['prg'] = "SYS"
        system_match = build_font_file_name(font_path, data)
        if os.path.exists(system_match):
            warn(f"Font {name} not found, substituting {system_match}")
            return system_match
    # Can't find the font, try the fallback
    fallback = get_fallback_font(font_path)
    warn(f"Font {name} not found, using fallback {fallback}")
    return fallback


class Font():
    """Represents a Stanford format font file."""
    NUM_GLYPHS = 128

    def __init__(self, font_name, file_name=None):
        self.font_name = font_name
        if not file_name:
            file_name = find_font(font_name)
        self.file_name = file_name
        words = self.load_file(self.file_name)
        self.decode_words(words)

    def load_file(self, file_name):
        """Read 36 octal words from given file."""
        if not os.path.exists(file_name):
            error(f"Font file {file_name} not found")
        words = []
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                for line in f.read().splitlines():
                    val = int(line, 8)
                    words.append(val)
        except ValueError:
            error("Error: Input does not follow 36-bit octal format.")
        if len(words) < 255:
            error("Font file too shortt.")
        return words

    def decode_words(self, words):
        """Get font data from list of words."""
        self.glyphs = []
        for word in words[:0o200]:
            width, ptr = split_18(word)
            _, word_count = split_18(words[ptr])
            self.glyphs.append(Glyph(self.font_name,
                                     width, words[ptr:ptr+word_count+2]))

        self.char_set_number = words[0o200]
        self.height = words[0o201]
        self.max_width = words[0o202]
        self.baseline = words[0o203]

        packed_description = words[0o240:0o377]
        self.description = packed_sail_ascii_to_utf8(
            packed_description).rstrip()

    def get_glyph(self, char_code):
        """Return the bitmap for the given character code."""
        return self.glyphs[char_code]

    def dump(self):
        """Print details about the font."""
        print(f"Font {self.font_name}")
        print(f"   Loaded from: {self.file_name}")
        print(f"   Description: {self.description}")
        print(f"   Height:      {self.height}")
        print(f"   Max width:   {self.max_width}")
        print(f"   Baseline     {self.baseline}")
        num_glyphs = len([g for g in self.glyphs if g.width > 0])
        print(f"   Glyphs:      {num_glyphs}")
