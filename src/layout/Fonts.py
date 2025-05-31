import tkinter
from tkinter.font import Font
from typing import Literal

FONTS = {}


def get_font(size: int, weight: Literal["normal", "bold"], style: Literal["roman", "italic"]) -> Font:
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight,
                                 slant=style)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]
