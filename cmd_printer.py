"""Class CmdPrinter outputs a printable representation of commands
that would be sent to the XGP prunter."""

# pylint: disable=too-many-public-methods, too-many-arguments
# pylint: disable=too-many-positional-arguments

import sys
from utils import sail_ascii_bytes_to_utf8
from printer import Printer


class CmdPrinter(Printer):
    """Output commands sent to the printer."""

    def __init__(self, output_file, options):
        self.output_file = output_file
        if self.output_file == '-':
            self.output = sys.stdout
        else:
            self.output = open(output_file, 'w', encoding='utf-8')
        self.options = options
        self.text = []

    def finish(self):
        """Finalise the printed material."""
        self.emit_text()
        self.output.close()

    def char(self, ch):
        """Add ch to the pending text."""
        self.text.append(ch)

    def emit_text(self):
        """Print text if any in buffer."""
        if len(self.text) > 0:
            s = sail_ascii_bytes_to_utf8(self.text)
            print(f"TEXT({s})", file=self.output)
            self.text = []

    def tab(self):
        """Process a tab command."""
        self.emit_text()
        print("TAB", file=self.output)

    def lf(self):
        """Process a line feed command."""
        self.emit_text()
        print("LF", file=self.output)

    def line_space(self, spacing):
        """Set line spacing"""
        self.emit_text()
        print(f"LINE_SPACE({spacing})", file=self.output)

    def ff(self):
        """Process a form feed command."""
        self.emit_text()
        print("FF", file=self.output)

    def cr(self):
        """Process a carriage return command."""
        self.emit_text()
        print("CR", file=self.output)

    def font_select(self, n):
        """Change font to the item indicated by n. Load if not already
        present."""
        self.emit_text()
        print(f"FONT_SELECT({n})", file=self.output)

    def font_select_align_top(self, n):
        """Select font n and align with previous text on the line."""
        self.emit_text()
        print(f"FONT_SELECT_ALIGN_TOP({n})", file=self.output)

    def column_select(self, col):
        """Set the absolute column to print at next"""
        self.emit_text()
        print(f"COLUMN_SELECT({col})", file=self.output)

    def baseline_adjust(self, adjustment):
        """Adjust the baseline for the current font. +ve means superscript"""
        self.emit_text()
        print(f"BASELINE_ADJUST({adjustment})", file=self.output)

    def relative_baseline_adjust(self, adjustment):
        """Adjust the baseline relative to previos adjustments."""
        self.emit_text()
        print(f"RELATIVE_BASELINE_ADJUST({adjustment})", file=self.output)

    def print_page_number(self):
        """Print the current page number"""
        self.emit_text()
        print("PRINT_PAGE_NUMBER", file=self.output)

    def accept_header_and_print(self, hdr):
        """Print the given header now and after each FF"""
        self.emit_text()
        s = sail_ascii_bytes_to_utf8(hdr)
        print(f"ACCEPT_HEADER_AND_PRINT({s})", file=self.output)

    def set_interchar_spacing(self, ics):
        """Set the inter-character spacing"""
        # From the UUO manual:
        # The next byte is interpreted as the intercharacter spacing,
        # which is not currently used for anything. This code is
        # included for compatibility with MIT.
        self.emit_text()
        print(f"SET_INTERCHAR_SPACING({ics})", file=self.output)

    def start_underline(self):
        """Remember the current column as the beginning of a section
        to be underlines."""
        self.emit_text()
        print("START_UNDERLINE", file=self.output)

    def stop_underline(self, rel_scan_line):
        """Draw an underline from the previously places underline mark"""
        self.emit_text()
        print(f"STOP_UNDERLINE({rel_scan_line})", file=self.output)

    def stop_underline_of_thickness(self, thickness, rel_scan_line):
        """Draw an underline of given thickness from the previously
        places underline mark"""
        self.emit_text()
        print(f"STOP_UNDERLINE_OF_THICKNESS({thickness}, {rel_scan_line})",
              file=self.output)

    def underscore(self, rel_scan_line, length):
        """Draw an underscore of given length on the scan line
        adjusted by rel_scan_line."""
        self.emit_text()
        print(f"UNDERSCORE({rel_scan_line}, {length})", file=self.output)

    def column_increment(self, increment):
        """Adjust the column to print text at"""
        self.emit_text()
        print(f"COLUMN_INCREMENT({increment})", file=self.output)

    def set_scan_line(self, scan_line):
        """Place text at the given scan line"""
        self.emit_text()
        print(f"SET_SCAN_LINE({scan_line})", file=self.output)

    def draw_vector(self, y0, x0, dx, n, w):
        """Draw a vector at the given position."""
        self.emit_text()
        print(f"DRAW_VECTOR({x0}, {y0}, {dx}, {n}, {w})", file=self.output)
