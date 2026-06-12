def move_sheet(items: list, index_from: int, index_to: int) -> None:
    items[index_from], items[index_to] = items[index_to], items[index_from]

