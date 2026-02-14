from typing import List, Dict, Any

MAX_CAPTION_CHARS: int = 950


def get_stock_lines(stock: Dict[str, Dict[str, Dict[str, Any]]]) -> List[str]:
    lines: List[str] = []
    for ptype in sorted(stock.keys()):
        lines.append(f"{ptype}:")
        for color in sorted(stock[ptype].keys()):
            meta = stock[ptype][color]
            price = meta.get("price", 0)
            qty = meta.get("qty", 0)
            lines.append(f"  • {color} — {qty} шт — {price} ₽/шт")
        lines.append("")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def paginate_lines(lines: List[str], max_chars: int = MAX_CAPTION_CHARS) -> List[List[str]]:
    pages: List[List[str]] = []
    cur: List[str] = []
    cur_len = 0
    for line in lines:
        add = len(line) + 1
        if cur and cur_len + add > max_chars:
            pages.append(cur)
            cur, cur_len = [], 0
        cur.append(line)
        cur_len += add
    if cur:
        pages.append(cur)
    return pages


def build_captions(pages: List[List[str]]) -> List[str]:
    captions: List[str] = []
    total = max(1, len(pages))
    for i, plines in enumerate(pages, start=1):
        body = "\n".join(plines) if plines else "Пусто."
        captions.append(f"📦 Склад пластика\n\n{body}\n\nСтраница {i}/{total}")
    return captions


def get_stock_pages(stock: Dict[str, Dict[str, Dict[str, Any]]]) -> List[str]:
    return build_captions(paginate_lines(get_stock_lines(stock)))
