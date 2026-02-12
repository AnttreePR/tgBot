"""Utilities for formatting and paginating stock data.

Telegram enforces a limit on the length of message captions (typically
around 1024 characters). To display the filament inventory in a user
friendly way without exceeding this limit, the stock data is split into
multiple pages. This module provides functions to format the stock
information into pages and to generate captions for each page, including
page numbers.

Functions:
    get_stock_lines(stock: dict[str, dict[str, int]]) -> list[str]: Flatten
        nested stock data into a list of human‑readable lines.
    paginate_lines(lines: list[str], max_chars: int) -> list[list[str]]:
        Group lines into pages such that the total character count per page
        stays below the max_chars threshold.
    build_captions(pages: list[list[str]]) -> list[str]: Turn pages of
        lines into caption strings with headers and page counters.
    get_stock_pages() -> list[str]: Convenience wrapper that loads the
        current stock and returns a list of ready‑to‑display captions.
"""

from typing import List, Dict

from .stock_data import get_stock

# Telegram currently limits media captions to roughly 1024 characters.
# Reserve some space for page numbering and other formatting by using a
# slightly smaller limit for the dynamic portion.
MAX_CAPTION_CHARS: int = 950

def get_stock_lines(stock: Dict[str, Dict[str, int]]) -> List[str]:
    """Flatten stock data into a list of human‑readable lines.

    Each filament type is printed on its own line followed by its colours on
    subsequent indented lines. A blank line is inserted between types for
    readability.

    Args:
        stock: Nested mapping of filament types to colours and quantities.

    Returns:
        List[str]: A sequence of lines representing the entire stock.
    """
    lines: List[str] = []
    for filament_type, colours in stock.items():
        lines.append(f"{filament_type}:")
        for colour, quantity in colours.items():
            lines.append(f"  • {colour} — {quantity}")
        # Insert an empty line after each type to separate sections
        lines.append("")
    # Remove the last blank line to avoid unnecessary spacing at the end
    if lines and lines[-1] == "":
        lines.pop()
    return lines

def paginate_lines(lines: List[str], max_chars: int = MAX_CAPTION_CHARS) -> List[List[str]]:
    """Divide a list of lines into pages based on character count.

    Telegram caption limits require that the combined length of all lines in
    a page does not exceed a certain threshold. This function accumulates
    lines until adding the next line would surpass the limit, then starts a
    new page. It ensures that no page is empty.

    Args:
        lines: List of strings representing the entire stock.
        max_chars: Maximum number of characters allowed per page (excluding
            page numbering and headers).

    Returns:
        List[List[str]]: A list of pages, where each page is a list of lines.
    """
    pages: List[List[str]] = []
    current_page: List[str] = []
    current_length: int = 0
    for line in lines:
        # +1 accounts for the newline character that will join lines
        additional_length = len(line) + 1
        # If adding this line would exceed the limit and the current page
        # already has content, push the current page and start a new one.
        if current_page and current_length + additional_length > max_chars:
            pages.append(current_page)
            current_page = []
            current_length = 0
        current_page.append(line)
        current_length += additional_length
    # Append any remaining lines as the final page
    if current_page:
        pages.append(current_page)
    return pages

def build_captions(pages: List[List[str]]) -> List[str]:
    """Construct caption strings for each page with headers and page numbers.

    Args:
        pages: A list of pages, where each page is a list of lines.

    Returns:
        List[str]: A list of caption strings ready for Telegram.
    """
    captions: List[str] = []
    total_pages = len(pages)
    for index, page_lines in enumerate(pages, start=1):
        # Join lines with newlines and add a header and footer with page info
        body = "\n".join(page_lines)
        caption = (
            "📦 Склад пластика\n\n"  # header
            f"{body}\n\n"  # body
            f"Страница {index}/{total_pages}"
        )
        captions.append(caption)
    return captions

def get_stock_pages() -> List[str]:
    """Generate all stock pages from the current inventory.

    Returns:
        List[str]: A list of caption strings with paginated stock data.
    """
    stock = get_stock()
    lines = get_stock_lines(stock)
    pages = paginate_lines(lines)
    return build_captions(pages)
