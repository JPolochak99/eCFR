from cfr_exporter.sanitize_names import sanitize_sheet_name

def unique_sheet_name(name: str, used_names: set[str]) -> str:
    base = sanitize_sheet_name(name)

    if base not in used_names:
        used_names.add(base)
        return base

    i = 2
    while True:
        suffix = f"_{i}"
        candidate = base[: 31 - len(suffix)] + suffix
        if candidate not in used_names:
            used_names.add(candidate)
            return candidate
        i += 1