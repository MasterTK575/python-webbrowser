import tkinter
from tkinter.font import Font
from typing import Literal

from src.Utils import Tag, Text

WIDTH, HEIGHT = 800, 600
HORIZONTAL_STEP, VERTICAL_STEP = 13, 18
FONTS = {}


class Layout:
    def __init__(self, tokens: list[Text | Tag]):
        self.display_list = []
        self.line = []
        self.cursor_x = HORIZONTAL_STEP
        self.cursor_y = VERTICAL_STEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 12

        for tok in tokens:
            if isinstance(tok, Text):
                self.words(tok)

            elif isinstance(tok, Tag):
                self.tags(tok)

        self.flush()

    def flush(self):
        if not self.line:
            return
        metrics = [font.metrics() for _, _, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent

        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))

        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent

        self.cursor_x = HORIZONTAL_STEP
        self.line = []

    def words(self, tok: Text):
        for word in tok.text.split():
            font = get_font(self.size, self.weight, self.style)
            word_width = font.measure(word)

            if self.cursor_x + word_width + HORIZONTAL_STEP > WIDTH:
                self.flush()

            self.line.append((self.cursor_x, word, font))
            self.cursor_x += word_width + font.measure(" ")

    def tags(self, tok: Tag):
        if tok.tag == "i":
            self.style = "italic"
        elif tok.tag == "/i":
            self.style = "roman"
        elif tok.tag == "b":
            self.weight = "bold"
        elif tok.tag == "/b":
            self.weight = "normal"
        elif tok.tag == "small":
            self.size -= 2
        elif tok.tag == "/small":
            self.size += 2
        elif tok.tag == "big":
            self.size += 4
        elif tok.tag == "/big":
            self.size -= 4
        elif tok.tag == "br":
            self.flush()
        elif tok.tag == "/p":
            self.flush()
            self.cursor_y += VERTICAL_STEP  # for extra gap in paragraphs


def get_font(size: int, weight: Literal["normal", "bold"], style: Literal["roman", "italic"]) -> Font:
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight,
                                 slant=style)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]
