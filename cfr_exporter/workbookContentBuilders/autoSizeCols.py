from openpyxl.utils import get_column_letter

def autosize_worksheet_cols(ws) -> None:
    for column_cells in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column_cells[0].column)
        for cell in column_cells:
            try:
                value = "" if cell.value is None else str(cell.value)
                max_length = max(max_length, len(value))
            except Exception:
                pass
            ws.column_dimensions[column_letter].width = min(max_length + 2, 60)