"""Read commands from a Document and send to a Printer."""

# pylint: disable=too-many-branches


from utils import info


def unexpected(message):
    """Print debug info if we get an unexpected sequence."""
    info(f"Unexpected printer instruction: {message}")


def execute(doc, printer):
    """Main work of program: read data from the input document and
        write to the printer based onn XGP format instructions."""
    while not doc.at_end():
        ch = doc.next()
        match ch:
            case 0:
                continue
            case 0o11:
                printer.tab()
            case 0o12:
                printer.lf()
            case 0o14:
                printer.ff()
            case 0o15:
                printer.cr()
            case 0o177:
                process_escape(doc, printer)
            case _:
                printer.char(ch)


def process_escape(doc, printer):
    """Process an escape character in the document."""
    ch = doc.next()
    if 0o16 <= ch <= 0o37:
        unexpected(f"ESCAPE: {ch:o}")
        return
    match ch:
        case 1:
            process_escape_1(doc, printer)
        case 2:
            process_escape_2(doc, printer)
        case 3:
            process_escape_3(doc, printer)
        case 4:
            process_escape_4(doc, printer)
        case 5:
            process_escape_5(doc, printer)
        case 6:
            process_escape_6(doc, printer)
        case 0o7 | 0o10 | 0o13:
            unexpected(f"ESCAPE: {ch:o}")
            return
        case _:
            printer.char(ch)


def process_escape_1(doc, printer):
    """Process an XGP ESCAPE 1 sequencxe."""
    ch = doc.next()
    if 0 <= ch <= 0o17:
        printer.font_select(ch)
        return
    match ch:
        case 0o40:
            col = doc.get_long_int() % 4096
            printer.column_select(col)
        case 0o41:
            rel_scan_line = doc.get_signed_int()
            length = doc.get_long_int() % 4096
            printer.underscore(rel_scan_line, length)
        case 0o42:
            spacing = doc.next()
            printer.line_space(spacing)
        case 0o43:
            adjustment = doc.get_signed_int()
            printer.baseline_adjust(adjustment)
        case 0o44:
            printer.print_page_number()
        case 0o45:
            size = doc.next()
            header = []
            for _ in range(size):
                hch = doc.next()
                header.append(hch)
            printer.accept_header_and_print(header)
        case 0o46:
            printer.start_underline()
        case 0o47:
            rel_scan_line = doc.get_signed_int()
            printer.stop_underline(rel_scan_line)
        case 0o50:
            ics = doc.next()
            printer.set_interchar_spacing(ics)
        case 0o51:
            thickness = doc.next()
            rel_scan_line = doc.get_signed_int()
            printer.stop_underline_of_thickness(thickness, rel_scan_line)
        case 0o52:
            adjustment = doc.get_signed_int()
            printer.relative_baseline_adjust(adjustment)
        case _:
            unexpected(f"XGP ESCAPE 1: {ch:o}")
            return


def process_escape_2(doc, printer):
    """Process an XGP ESCAPE 2 sequencxe."""
    increment = doc.get_signed_int()
    printer.column_increment(increment)


def process_escape_3(doc, printer):
    """Process an XGP ESCAPE 3 sequencxe."""
    scan_line = doc.get_long_int()
    printer.set_scan_line(scan_line)


def process_escape_4(doc, printer):
    """Process an XGP ESCAPE 4 sequencxe."""
    y0 = doc.get_long_int()
    x0 = doc.get_long_int()
    dx = doc.get_float()
    n = doc.get_long_int()
    w = doc.get_long_int()
    printer.draw_vector(y0, x0, dx, n, w)


# Note XGP escapes 5 and 6 are in UUO.UPD[S,DOC], not in UUO.ME
def process_escape_5(doc, printer):
    """Process an XGP ESCAPE 5 sequencxe."""
    ch = doc.next()
    printer.font_select(ch)


def process_escape_6(doc, printer):
    """Process an XGP ESCAPE 6 sequencxe."""
    ch = doc.next()
    printer.font_select_align_top(ch)
