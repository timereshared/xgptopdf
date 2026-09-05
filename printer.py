"""Abstract class to define Printer interface."""

# pylint: disable=too-many-public-methods, too-many-arguments
# pylint: disable=too-many-positional-arguments


from abc import ABC, abstractmethod


class Printer(ABC):
    """Abstract class to define Printer interface."""
    @abstractmethod
    def finish(self):
        """Finalise the printed material."""

    @abstractmethod
    def char(self, ch):
        """Add ch to the pending text."""

    @abstractmethod
    def tab(self):
        """Process a tab command."""

    @abstractmethod
    def lf(self):
        """Process a line feed command."""

    @abstractmethod
    def line_space(self, spacing):
        """Set line spacing"""

    @abstractmethod
    def ff(self):
        """Process a form feed command."""

    @abstractmethod
    def cr(self):
        """Process a carriage return command."""

    @abstractmethod
    def font_select(self, n):
        """Change font to the item indicated by n. Load if not already
        present."""

    @abstractmethod
    def font_select_align_top(self, n):
        """Select font n and align with previous text on the line."""

    @abstractmethod
    def column_select(self, col):
        """Set the absolute column to print at next"""

    @abstractmethod
    def baseline_adjust(self, adjustment):
        """Adjust the baseline for the current font. +ve means superscript"""

    @abstractmethod
    def relative_baseline_adjust(self, adjustment):
        """Adjust the baseline relative to previos adjustments."""

    @abstractmethod
    def print_page_number(self):
        """Print the current page number"""

    @abstractmethod
    def accept_header_and_print(self, hdr):
        """Print the given header now and after each FF"""

    @abstractmethod
    def set_interchar_spacing(self, ics):
        """Set the inter-character spacing"""
        # From the UUO manual:
        # The next byte is interpreted as the intercharacter spacing,
        # which is not currently used for anything. This code is
        # included for compatibility with MIT.

    @abstractmethod
    def start_underline(self):
        """Remember the current column as the beginning of a section
        to be underlines."""

    @abstractmethod
    def stop_underline(self, rel_scan_line):
        """Draw an underline from the previously places underline mark"""

    @abstractmethod
    def stop_underline_of_thickness(self, thickness, rel_scan_line):
        """Draw an underline of given thickness from the previously
        places underline mark"""

    @abstractmethod
    def underscore(self, rel_scan_line, length):
        """Draw an underscore of given length on the scan line
        adjusted by rel_scan_line."""

    @abstractmethod
    def column_increment(self, increment):
        """Adjust the column to print text at"""

    @abstractmethod
    def set_scan_line(self, scan_line):
        """Place text at the given scan line"""

    @abstractmethod
    def draw_vector(self, y0, x0, dx, n, w):
        """Draw a vector at the given position."""
