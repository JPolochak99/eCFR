def move_item(workbook_tables, index_from: int, index_to: int):
    workbook_tables[index_from], workbook_tables[index_to] = (
        workbook_tables[index_to],
        workbook_tables[index_from],
    )