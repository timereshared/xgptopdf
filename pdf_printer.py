"""Class PDFPrinter simulates the XGP, writing to a PDF."""

# pylint: disable=too-many-public-methods, too-many-locals
# pylint: disable=too-many-instance-attributes, too-many-arguments
# pylint: disable=too-many-positional-arguments,too-many-branches

from PIL import Image, ImageDraw

from font import Font
from printer import Printer
from utils import error, warn


class PDFPrinter(Printer):
    """Output a PDF based on text and drawing instructions."""
    DPI = 200                   # dots per inch resolution
    PAGE_WIDTH = 8.5            # inches
    PAGE_HEIGHT = 11            # inches
    TAB_STOP = 8                # characters per tab stop

    def __init__(self, output_file, options):
        self.output_file = output_file
        self.options = options
        if self.output_file == '-':
            error("Output to stdout not supported for PDF format")
        self.max_column = int(self.PAGE_WIDTH * self.DPI)
        self.max_scan_line = (self.options.top_page_margin +
                              self.options.page_body_size +
                              self.options.bottom_page_margin)
        self.fonts = {}
        self.font = None
        self.text = []          # list of characters pending output
        self.column = 0
        self.scan_line = 0
        self.line_height = 0    # max height of chars in current line
        self.start_underline_colum = 0
        self.baseline_adjustment = 0
        self.pages = []
        self.page_number = -1   # first page will be page 0
        self.new_page()
        # Needed for some docs that don't select their only font
        if self.options.font_names:
            self.font_select(min(self.options.font_names), emit=False)

    def new_page(self):
        """Start a new page."""
        self.page = Image.new('1', (self.max_column, self.max_scan_line),
                              'white')
        self.page_number += 1
        self.column = self.options.left_margin
        self.scan_line = self.options.top_page_margin
        self.line_height = 0
        self.start_underline_colum = 0

    def finish(self):
        """Finalise the printed material."""
        self.emit_text()
        if (self.column > self.options.left_margin or
           self.scan_line > self.options.top_page_margin):
            # Still some text on page and no final FF
            self.pages.append(self.page)
        self.pages[0].save(self.output_file, resolution=self.DPI,
                           save_all=True,
                           append_images=self.pages[1:])

    def char(self, ch):
        """Add ch to the pending text."""
        self.text.append(ch)

    def emit_text(self):
        """Print text if any in buffer."""
        if len(self.text) > 0:
            if (self.scan_line >
               self.max_scan_line - self.options.bottom_page_margin):
                # Force a new page, restoring the current column
                self.pages.append(self.page)
                old_column = self.column
                self.new_page()
                self.column = old_column
            for ch in self.text:
                self.draw_char(ch)
            self.text = []

    def draw_char(self, ch):
        """Draw character in current font at current position."""
        glyph = self.font.get_glyph(ch)
        column = self.column - glyph.left_kern
        scan_line = (self.scan_line + glyph.rows_from_top -
                     self.baseline_adjustment)
        glyph_image = glyph.get_image()
        # Preserve existing black pixels and add new black pixels from
        # the gluph by using the current contents of the page as a
        # mask for the paste. Is there a better way?
        current = self.page.crop((column, scan_line,
                                  column + glyph_image.width,
                                  scan_line + glyph_image.height))
        self.page.paste(glyph_image, (column, scan_line), current)
        self.line_height = max(self.font.height, self.line_height)
        self.column += glyph.width

    def tab(self):
        """Process a tab command."""
        self.emit_text()
        space_width = self.font.get_glyph(ord(' ')).width
        current_space_column = (self.column - self.options.left_margin
                                ) / space_width
        next_tab = current_space_column + self.TAB_STOP - (
            current_space_column % self.TAB_STOP)
        next_tab_column = self.options.left_margin + (next_tab * space_width)
        self.column = int(next_tab_column)

    def lf(self):
        """Process a line feed command."""
        self.emit_text()
        self.scan_line += self.line_height + self.options.interline_spacing
        self.line_height = self.font.height

    def line_space(self, spacing):
        """Set line spacing"""
        self.emit_text()
        self.scan_line += self.line_height + spacing
        self.line_height = self.font.height

    def ff(self):
        """Process a form feed command."""
        self.emit_text()
        self.pages.append(self.page)
        self.new_page()

    def cr(self):
        """Process a carriage return command."""
        self.emit_text()
        self.column = self.options.left_margin

    def font_select(self, n, emit=True):
        """Change font to the item indicated by n. Load if not already
        present."""
        if emit:
            self.emit_text()
        if n not in self.fonts:
            self.load_font(n)
        self.font = self.fonts[n]
        self.baseline_adjustment = 0

    def font_select_align_top(self, n):
        """Select font n and align with previous text on the line."""
        self.emit_text()
        # From  UUO.UPD[S,DOC], not in UUO.ME
        # 208.  XGP ESCAPE 6 is "select font and align at top
        #       A relative baseline adjust is done to make the newly
        #       selected font line up at the top with the top of the
        #       previously selected font, unless no chars have been output
        #       on the current text line, in which case XGP ESCAPE 6 is
        #       the same as XGP ESCAPE 5 (font select).
        # TODO: not sure how to do this, as glyphs already align at the top?
        self.font_select(n)

    def load_font(self, n):
        """Read in font n from disk file."""
        if n not in self.options.font_names:
            error(f"Error: font {n} not defined.")
        self.fonts[n] = Font(self.options.font_names[n])
        self.font = self.fonts[n]

    def column_select(self, col):
        """Set the absolute column to print at next"""
        self.emit_text()
        self.column = col

    def baseline_adjust(self, adjustment):
        """Adjust the baseline for the current font. +ve means superscript"""
        self.emit_text()
        self.baseline_adjustment = adjustment

    def relative_baseline_adjust(self, adjustment):
        """Adjust the baseline relative to previos adjustments."""
        self.emit_text()
        self.baseline_adjustment += adjustment

    def print_page_number(self):
        """Print the current page number"""
        self.emit_text()
        for num in f"{self.page_number}":
            self.char(num)

    def accept_header_and_print(self, hdr):
        """Print the given header now and after each FF"""
        self.emit_text()
        warn("Unimplemented command ACCEPT_HEADER_AND_PRINT")

    def set_interchar_spacing(self, ics):
        """Set the inter-character spacing"""
        # From the UUO manual:
        # The next byte is interpreted as the intercharacter spacing,
        # which is not currently used for anything. This code is
        # included for compatibility with MIT.
        self.emit_text()
        warn("Unimplemented command SET_INTERCHAR_SPACING")

    def start_underline(self):
        """Remember the current column as the beginning of a section
        to be underlines."""
        self.emit_text()
        self.start_underline_colum = self.column

    def stop_underline(self, rel_scan_line):
        """Draw an underline from the previously places underline mark"""
        self.emit_text()
        self.draw_underline(1, rel_scan_line)

    def stop_underline_of_thickness(self, thickness, rel_scan_line):
        """Draw an underline of given thickness from the previously
        places underline mark"""
        self.emit_text()
        self.draw_underline(thickness, rel_scan_line)

    def underscore(self, rel_scan_line, length):
        """Draw an underscore of given length on the scan line
        adjusted by rel_scan_line."""
        self.emit_text()
        old = self.start_underline_colum
        self.start_underline_colum = self.column - length
        self.draw_underline(1, rel_scan_line)
        self.start_underline_colum = old

    def draw_underline(self, thickness, rel_scan_line):
        """Implementation of underlining"""
        # Not clear if baseline_adjustment should be taken into acount
        scan_line = self.scan_line + self.font.baseline + rel_scan_line
        draw = ImageDraw.Draw(self.page)
        draw.line((self.start_underline_colum, scan_line,
                   self.column, scan_line), fill='black', width=thickness)

    def column_increment(self, increment):
        """Adjust the column to print text at"""
        self.emit_text()
        self.column += increment

    def set_scan_line(self, scan_line):
        """Place text at the given scan line"""
        self.emit_text()
        self.scan_line = scan_line

    def draw_vector(self, y0, x0, dx, n, w):
        """Draw a vector at the given position."""
        self.emit_text()
        draw = ImageDraw.Draw(self.page)
        for i in range(n):
            current_y = y0 + i
            current_x = x0 + (i * dx)

            # Define the bounding box for the rectangle at this scan line
            # (x_min, y_min, x_max, y_max)
            left = current_x
            top = current_y
            right = current_x + w
            bottom = current_y

            draw.line([left, top, right, bottom], fill="black")
