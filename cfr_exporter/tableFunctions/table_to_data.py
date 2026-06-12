import pandas as pd
from bs4 import BeautifulSoup

def table_html_to_df(table_html: str) -> pd.DataFrame:
    soup = BeautifulSoup(table_html, "xml")
    table = soup.find("TABLE") or soup.find("table")
    if table is None:
        raise ValueError("Could not parse selected table.")

    body = table.find("TBODY") or table.find("tbody")
    tr_source = body.find_all(["TR", "tr"]) if body else table.find_all(["TR", "tr"])

    rows = []
    for tr in tr_source:
        # Skip header rows inside body.
        if tr.find_all(["TH", "th"]) and not tr.find_all(["TD", "td"]):
            continue

        cells = [
            cell.get_text(" ", strip=True)
            for cell in tr.find_all(["TD", "td"])
        ]

        if cells:
            rows.append(cells)

    if not rows:
        raise ValueError("No rows found in the selected table.")

    max_cols = max(len(r) for r in rows)
    rows = [r + [""] * (max_cols - len(r)) for r in rows]

    headers = _build_multirow_headers(table, max_cols)

    if headers:
        headers = headers[:max_cols]

        # Remove duplicated header row from data if present.
        if rows:
            first_row = [str(x).strip() for x in rows[0]]
            header_row = [str(x).strip() for x in headers[: len(first_row)]]
            if first_row == header_row:
                rows = rows[1:]
    else:
        headers = [f"Column {i}" for i in range(1, max_cols + 1)]

    return pd.DataFrame(rows, columns=headers)




def _get_span(cell, name: str) -> int:
    value = cell.get(name) or cell.get(name.lower()) or 1
    try:
        return int(value)
    except ValueError:
        return 1


def _extract_header_rows(table):
    thead = table.find("THEAD") or table.find("thead")
    if thead:
        return thead.find_all(["TR", "tr"])

    header_rows = []
    for tr in table.find_all(["TR", "tr"]):
        if tr.find_all(["TH", "th"]):
            header_rows.append(tr)
        elif header_rows:
            break

    return header_rows


def _build_multirow_headers(table, max_cols: int) -> list[str] | None:
    header_rows = _extract_header_rows(table)

    if not header_rows:
        return None

    grid = []

    for row_idx, tr in enumerate(header_rows):
        while len(grid) <= row_idx:
            grid.append([""] * max_cols)

        col_idx = 0
        for cell in tr.find_all(["TH", "TD", "th", "td"]):
            while col_idx < max_cols and grid[row_idx][col_idx]:
                col_idx += 1

            text = cell.get_text(" ", strip=True)
            colspan = _get_span(cell, "COLSPAN")
            rowspan = _get_span(cell, "ROWSPAN")

            for r in range(rowspan):
                while len(grid) <= row_idx + r:
                    grid.append([""] * max_cols)

                for c in range(colspan):
                    if col_idx + c < max_cols:
                        grid[row_idx + r][col_idx + c] = text

            col_idx += colspan

    headers = []
    for col in range(max_cols):
        parts = []
        for row in grid:
            if col < len(row):
                value = str(row[col]).strip()
                if value and value not in parts:
                    parts.append(value)

        headers.append(" ".join(parts).strip() or f"Column {col + 1}")

    return headers