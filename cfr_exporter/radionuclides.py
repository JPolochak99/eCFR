from __future__ import annotations

import re

import pandas as pd

ELEMENT_NAME_TO_SYMBOL = {
    "hydrogen": "H",
    "helium": "He",
    "lithium": "Li",
    "beryllium": "Be",
    "boron": "B",
    "carbon": "C",
    "nitrogen": "N",
    "oxygen": "O",
    "fluorine": "F",
    "neon": "Ne",
    "sodium": "Na",
    "magnesium": "Mg",
    "aluminum": "Al",
    "silicon": "Si",
    "phosphorus": "P",
    "sulfur": "S",
    "chlorine": "Cl",
    "argon": "Ar",
    "potassium": "K",
    "calcium": "Ca",
    "scandium": "Sc",
    "titanium": "Ti",
    "vanadium": "V",
    "chromium": "Cr",
    "manganese": "Mn",
    "iron": "Fe",
    "cobalt": "Co",
    "nickel": "Ni",
    "copper": "Cu",
    "zinc": "Zn",
    "gallium": "Ga",
    "germanium": "Ge",
    "arsenic": "As",
    "selenium": "Se",
    "bromine": "Br",
    "krypton": "Kr",
    "rubidium": "Rb",
    "strontium": "Sr",
    "yttrium": "Y",
    "zirconium": "Zr",
    "niobium": "Nb",
    "molybdenum": "Mo",
    "technetium": "Tc",
    "ruthenium": "Ru",
    "rhodium": "Rh",
    "palladium": "Pd",
    "silver": "Ag",
    "cadmium": "Cd",
    "indium": "In",
    "tin": "Sn",
    "antimony": "Sb",
    "tellurium": "Te",
    "iodine": "I",
    "xenon": "Xe",
    "cesium": "Cs",
    "caesium": "Cs",
    "barium": "Ba",
    "lanthanum": "La",
    "cerium": "Ce",
    "praseodymium": "Pr",
    "neodymium": "Nd",
    "promethium": "Pm",
    "samarium": "Sm",
    "europium": "Eu",
    "gadolinium": "Gd",
    "terbium": "Tb",
    "dysprosium": "Dy",
    "holmium": "Ho",
    "erbium": "Er",
    "thulium": "Tm",
    "ytterbium": "Yb",
    "lutetium": "Lu",
    "hafnium": "Hf",
    "tantalum": "Ta",
    "tungsten": "W",
    "rhenium": "Re",
    "osmium": "Os",
    "iridium": "Ir",
    "platinum": "Pt",
    "gold": "Au",
    "mercury": "Hg",
    "thallium": "Tl",
    "lead": "Pb",
    "bismuth": "Bi",
    "polonium": "Po",
    "astatine": "At",
    "radon": "Rn",
    "francium": "Fr",
    "radium": "Ra",
    "actinium": "Ac",
    "thorium": "Th",
    "protactinium": "Pa",
    "uranium": "U",
    "neptunium": "Np",
    "plutonium": "Pu",
    "americium": "Am",
    "curium": "Cm",
    "berkelium": "Bk",
    "californium": "Cf",
    "einsteinium": "Es",
    "fermium": "Fm",
    "mendelevium": "Md",
    "nobelium": "No",
    "lawrencium": "Lr",
    "rutherfordium": "Rf",
    "dubnium": "Db",
    "seaborgium": "Sg",
    "bohrium": "Bh",
    "hassium": "Hs",
    "meitnerium": "Mt",
    "darmstadtium": "Ds",
    "roentgenium": "Rg",
    "copernicium": "Cn",
    "nihonium": "Nh",
    "flerovium": "Fl",
    "moscovium": "Mc",
    "livermorium": "Lv",
    "tennessine": "Ts",
    "oganesson": "Og",
}

RADIONUCLIDE_SYMBOL_RE = re.compile(r"^([A-Z][a-z]?)-(\d+)([A-Za-z]*)$")
RADIONUCLIDE_NAME_RE = re.compile(r"^([A-Za-z][A-Za-z\s\-]+?)[\s\-]+(\d+)([A-Za-z]*)$")


def is_radionuclide_column(column_name: str) -> bool:
    name = str(column_name).lower()
    return "symbol" in name or "radionuclide" in name or "chemical" in name


def parse_radionuclide(value):
    if pd.isna(value):
        return value, "", "", ""

    s = str(value).strip()

    notes = re.findall(r"\(([^)]*)\)", s)
    footnotes = []
    descriptions = []

    for note in notes:
        note = note.strip().strip(",.; ")
        if re.fullmatch(r"[A-Za-z]", note):
            footnotes.append(note)
        else:
            descriptions.append(note)

    note_text = "; ".join(descriptions)
    footnote_text = ", ".join(footnotes)

    core = re.sub(r"\s*\([^)]*\)", "", s)
    core = re.sub(r"\s*,\s*", " ", core).strip()
    core = core.rstrip(",.; ")

    m = RADIONUCLIDE_SYMBOL_RE.match(core)
    if m:
        symbol = m.group(1)
        mass = m.group(2).zfill(3)
        suffix = m.group(3)
        formatted = f"{mass}{symbol}{suffix}"
        return formatted, note_text, footnote_text, core

    m = RADIONUCLIDE_NAME_RE.match(core)
    if m:
        element_name = m.group(1).strip().lower()
        symbol = ELEMENT_NAME_TO_SYMBOL.get(element_name)
        if symbol:
            mass = m.group(2).zfill(3)
            suffix = m.group(3)
            formatted = f"{mass}{symbol}{suffix}"
            return formatted, note_text, footnote_text, core

    return s, note_text, footnote_text, core
