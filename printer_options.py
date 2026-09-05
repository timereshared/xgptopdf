"""PrinterOptions is used to set options such as fonts and margins,
which may come from the document or from the user.
"""

# pylint: disable=too-many-branches,too-many-instance-attributes
from utils import error, info, warn


class PrinterOptions():
    """Options for the printer - fonts, margins etc - that can come
    from the document or the command line."""

    def __init__(self, doc_options, cmdline_options):
        self.font_names = {}
        # Defaults from UUO.ME[S,DOC]
        self.top_page_margin = 200
        self.page_body_size = 1796  # 1800 in later editions of the UUO
        self.bottom_page_margin = 200
        self.left_margin = 200
        self.right_margin = 1650
        self.interline_spacing = 4
        self.from_tex = False
        self.merge_options(doc_options)
        self.merge_options(cmdline_options)
        if not self.font_names:
            warn("No fonts defined")
            self.font_names[0] = "(missing)"
        # Zero page body size meant print as a long scroll of paper
        # but this is not practical for PDFs, especially as we need to
        # know the length before we start printing. In this case, set
        # height to be US Legal (2800 pixels)
        if self.page_body_size == 0:
            self.page_body_size = 2800 - (self.bottom_page_margin +
                                          self.top_page_margin)
            info("Overridden zero page_body_size")

    def dump(self):
        """Print out the current set of options."""
        info("Printer options")
        info(f"    top_page_margin: {self.top_page_margin}")
        info(f"    page_body_size: {self.page_body_size}")
        info(f"    bottom_page_margin: {self.bottom_page_margin}")
        info(f"    left_margin: {self.left_margin}")
        info(f"    right_margin: {self.right_margin}")
        info(f"    interline_spacing: {self.interline_spacing}")
        info(f"    from TeX: {self.from_tex}")
        info("    Font names:")
        for index, f in self.font_names.items():
            info(f"        #{index}: {f}")

    def merge_options(self, options):
        """Add options to the current set, replacing any already set,"""
        for key, value in options.items():
            if key == "USETI" and value.find("*TEX*") > 0:
                # Used by TeX to indicates extended font options
                # which we have already read.
                self.from_tex = True
                continue
            if key == 'NOWRAPAROUND':
                info(f"Printer option {key} ignored")
                continue
            if key.startswith('FONT'):
                self.merge_font(key, value)
                continue
            try:
                num = int(value)
            except ValueError:
                error(f"Value not an integer for option {key}")
            if key == "TMAR":
                self.top_page_margin = num
            elif key == 'PMAR':
                self.page_body_size = num
            elif key == 'BMAR':
                self.bottom_page_margin = num
            elif key == 'LMAR':
                self.left_margin = num
            elif key == 'RMAR':
                self.right_margin = num
            elif key == 'XLINE':
                self.interline_spacing = num
            elif key in {'NTNODE', 'NVNODE'}:
                # On WAITS XSPOOL, these options were used to control
                # the number of buffers for text and vectors. On this
                # implementation there is no limit, so these can be
                # ignored.
                continue
            else:
                warn(f"Ignoring invalid option {key}={value}")

    def merge_font(self, key, value):
        """Set a font based on key and value."""
        # Key is "FONT#nn from document options and
        # "FONT-nn" from the command line.
        num = key[5:]
        try:
            index = int(num)
            # If it's a WAITS name rather than a host path
            if value.find('/') == -1:
                # Remove spaces and make upper case
                value = "".join(value.split()).upper()
            self.font_names[index] = value
        except ValueError:
            error(f"Font index not a number for option {key}")
