"""The Glyph class represents a single font character."""

# pylint: disable=too-many-locals,too-many-instance-attributes

from PIL import Image

from utils import split_9, split_18, warn


def signed_9(val):
    """Treat the value as a signed 9 bit number."""
    if val & 0x100:
        return val - 512
    return val


def extract_bits(words, element_size):
    """Take a list of 36 bit words and divide into a list of numbers
    each of element_size. Return a list of (inverted) bits,"""
    results = []

    if element_size <= 36:
        n = 36 // element_size
        mask = (1 << element_size) - 1
        for word in words:
            for i in range(n):
                # Extract pieces from left to right
                shift = 36 - ((i + 1) * element_size)
                val = (word >> shift) & mask
                results.append(val)
    else:
        # Number of 36-bit words needed per element
        words_per_element = (element_size + 35) // 36
        for i in range(0, len(words), words_per_element):
            chunk = words[i:i + words_per_element]
            if len(chunk) < words_per_element:
                break

            # Combine words into one long integer
            long_word = 0
            for word in chunk:
                long_word = (long_word << 36) | (word & 0xFFFFFFFFF)

            # Take the leftmost element_size bits
            total_bits = words_per_element * 36
            val = (long_word >> (total_bits - element_size)) & ((
                1 << element_size) - 1)
            results.append(val)

    # Convert to inverted binary bits
    final_output = []
    for val in results:
        # Convert to binary string padded to element_size
        bin_str = f"{val:0{element_size}b}"
        for bit in bin_str:
            # Append inverse (1 -> 0, 0 -> 1)
            final_output.append(1 if bit == '0' else 0)

    return final_output


class Glyph():
    """Represents a single character in a XGP font."""
    def __init__(self, font_name, width, words):
        self.font_name = font_name
        self.width = width
        self.decode_header(words)
        # Only decode the full data it if we actually need the bitmap
        # image of the glyph
        self.image = None

    def get_image(self):
        """Get the bitmap image for this glyph."""
        if not self.image:
            self.create_image()
        return self.image

    def decode_header(self, words):
        """Extract info from the header of the XGP font glyph."""
        self.raster_width, self.char_code, _, _ = split_9(words[0])
        _, word_count = split_18(words[0])
        hdr2 = split_9(words[1])
        lk, self.rows_from_top, _, self.data_row_count = hdr2
        self.left_kern = signed_9(lk)
        self.data_width = (self.width if self.raster_width == 0
                           else self.raster_width)
        self.packed_glyph = words[2:word_count]

    def create_image(self):
        """Extract data from words taken from a XGP font item."""
        if self.data_width == 0:
            warn(f"Font {self.font_name} glyph {self.char_code} empty")
            self.image = Image.new('1', (1, 1))
            return
        bits = extract_bits(self.packed_glyph, self.data_width)
        # Sometimes we get more bits in the buffer than we expect
        bits = bits[:self.data_row_count * self.data_width]
        self.image = Image.new('1', (self.data_width, self.data_row_count))
        self.image.putdata(bits)

    def debug_glyph(self, bits):
        """Temp debug stuff"""
        gchr = chr(self.char_code)
        print(f"Font {self.font_name} glyph {self.char_code} '{gchr}'")
        print(f"    width {self.width} ras width {self.raster_width}")
        print(f"    data # row {self.data_row_count} # col  {self.data_width}")
        drc = self.data_row_count * self.data_width
        print(f"    data r*c {drc} len(bits) {len(bits)}")
        print(f"    l kern {self.left_kern} rows f top {self.rows_from_top}")
        for y in range(self.data_row_count):
            buf = []
            for x in range(self.data_width):
                bit = bits[(y*self.data_width)+x]
                buf.append(" " if bit else '#')
            print("".join(buf))
