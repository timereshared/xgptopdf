"""The Document class represents a binary XGP spool file from WAITS."""

# The document has
# a) an option (but in practice always present) set of XGP options
#    marked by a '/' in the first char, extending up to the first FF
# b) a body which contains text and XGP instruction
# c) an optional extension containing more fornt settings. This is
#    used by TeX and signalled by a USETI in the options, but we
#    detect by looking for a sequence of nulls then "/FONT' at the
#    end of the document.

import re


from utils import split_7, sail_ascii_bytes_to_utf8, error, info


def remove_extra_slashes(text):
    """Remove /s, except for /FONT."""
    return re.sub(r'/(?!FONT)', '', text)


class Document():
    """Represents a XGP document as a stream of 7-bit bytes."""
    def __init__(self, lines):
        self.index = 0
        self.options = {}
        [body, extension] = self.split_extended_fonts(lines)
        self.chars = self.decode_octal_lines(body)
        self.size = len(self.chars)
        if self.peek() == ord('C'):
            # TV or E editor directory page: can skip but if the file
            # has been edited it is likely to be damaged.
            info("Skipping text editor directory")
            self.get_str_until(ord('\f'))
        if self.peek() == ord('/'):
            self.get_xgp_options(self.get_str_until(ord('\f')))
        if extension:
            words = self.decode_octal_lines(extension)
            text = sail_ascii_bytes_to_utf8(words)
            # Remove /s, except for /FONT.
            text = re.sub(r'/(?!FONT)', '', text)
            info("Font extension found")
            self.get_xgp_options(text)

    def at_end(self):
        """Return true if at end of document."""
        return self.index >= self.size

    def peek(self):
        """Return the next character but don't advance."""
        return self.chars[self.index]

    def next(self):
        """Return the next character in the document."""
        char = self.chars[self.index]
        self.index += 1
        return char

    def get_str_until(self, terminator):
        """Read chars up to but not including terminator. Return as
        string and advance index to the char after the terminator."""
        buf = []
        while self.peek() != terminator:
            buf.append(self.next())
        self.next()
        return sail_ascii_bytes_to_utf8(buf)

    def get_signed_int(self):
        """Read the next character and convert to a signed value."""
        value = self.next()
        if value & 0b01000000:
            return value - 128
        return value

    def get_long_int(self):
        """Read the next two characters and convert to a number."""
        return (self.next() << 7) + self.next()

    def get_float(self):
        """Take three bytes from the document and treat as 1 bit of
        sign; 11 bits of integer; 9 bits of fraction."""
        n = (self.next() << 14) + (self.next() << 7) + self.next()
        sign = -1 if (n >> 20) & 1 else 1
        integer_part = (n >> 9) & 0x7FF
        fractional_part = n & 0x1FF
        # Fractional part represents: val / 2^9 (512)
        return sign * (integer_part + (fractional_part / 512.0))

    def decode_octal_lines(self, lines):
        """Break down octaal numbers to an array of 7 bit bytes."""
        # Validate and Parse Octal
        octal_values = []
        try:
            for line in lines:
                for part in line.split():
                    # Ensure it's a valid octal number
                    val = int(part, 8)
                    octal_values.append(val)
        except ValueError:
            error("Error: Input does not follow 36-bit octal format.")

        # Convert into an list of char codes. (We don't convert from
        # SAIL ASCII to equivalent UTF-8 characters, as the values are
        # used for lookup in fonts).
        chars = []
        for word in octal_values:
            more = split_7(word)
            chars.extend(more)
        return chars

    def split_extended_fonts(self, lines):
        """Find any extended list of fonts at the end of the document.
        Return [body, extended] if so, otherwise [body, None]"""
        font_start = "276151747250"  # /FONT
        null_line = "000000000000"

        # Search from the end for the sequence
        if len(lines) > 2:
            for i in range(len(lines) - 2, 0, -1):
                if lines[i+1] == font_start and lines[i] == null_line:
                    # i is the index of '0000...'
                    return lines[:i+1], lines[i+1:]
        return lines, []

    def get_xgp_options(self, text):
        """Read options set in the XGP page."""
        opts = text.strip().split('/')
        for opt in opts:
            if opt == "":
                continue
            if opt.find('=') < 0:
                self.options[opt] = True
            else:
                # If opt is "a=b=c" just get a and b
                key, val = opt.split('=')[:2]
                self.options[key] = val
