import pandas as pd
from bs4 import BeautifulSoup

def table_html_to_df(table_html: str) -> pd.DataFrame:
    """Parse one eCFR table into a DataFrame without assuming a fixed schema."""
    soup = BeautifulSoup(table_html, "xml")
    table = soup.find("TABLE") or soup.find("table")
    if table is None:
        raise ValueError("Could not parse selected table.")

    body = table.find("TBODY")
    tr_source = body.find_all("TR") if body else table.find_all("TR")

    rows = []
    for tr in tr_source:
        cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["TD", "TH"])]
        if cells:
            rows.append(cells)

    if not rows:
        raise ValueError("No rows found in the selected table.")

    headers = None
    thead = table.find("THEAD")
    if thead:
        header_tr = thead.find("TR")
        if header_tr:
            headers = [cell.get_text(" ", strip=True) for cell in header_tr.find_all(["TH", "TD"])]

    if headers is None:
        for tr in tr_source:
            if tr.find_all("TH"):
                headers = [cell.get_text(" ", strip=True) for cell in tr.find_all(["TH", "TD"])]
                break

    max_cols = max(len(r) for r in rows)
    rows = [r + [""] * (max_cols - len(r)) for r in rows]

    if headers:
        headers = [h if h else f"Column {i}" for i, h in enumerate(headers, start=1)]
        headers = headers + [f"Column {i}" for i in range(len(headers) + 1, max_cols + 1)]

        if rows and len(rows[0]) == len(headers[: len(rows[0])]):
            first_row = [str(x).strip() for x in rows[0]]
            header_row = [str(x).strip() for x in headers[: len(first_row)]]
            if first_row == header_row:
                rows = rows[1:]

        return pd.DataFrame(rows, columns=headers[:max_cols])

    columns = [f"Column {i}" for i in range(1, max_cols + 1)]
    return pd.DataFrame(rows, columns=columns)