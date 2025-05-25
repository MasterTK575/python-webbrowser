from __future__ import annotations

import tkinter
from tkinter.font import Font
from typing import Literal

from src.DrawRect import DrawRect
from src.DrawText import DrawText
from src.Element import Element
from src.Text import Text

FONTS = {}

BLOCK_ELEMENTS = [
    "html", "body", "article", "section", "nav", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
    "footer", "address", "p", "hr", "pre", "blockquote",
    "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure",
    "figcaption", "main", "div", "table", "form", "fieldset",
    "legend", "details", "summary"
]


class BlockLayout:
    def __init__(self, node: Element, parent, previous: BlockLayout | None) -> None:
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []
        self.display_list = []

        self.line = None
        self.size = None
        self.style = None
        self.weight = None
        self.cursor_y = None
        self.cursor_x = None
        self.x = None
        self.y = None
        self.width = None
        self.height = None

    # width: top-down calculation
    # height: bottom-up calculation
    def layout(self):
        if self.previous:  # if there is a previous block, position this one below it
            self.y = self.previous.y + self.previous.height
        else:  # first child element starts at same y position as the parent
            self.y = self.parent.y
        self.x = self.parent.x  # horizontal position always the same as the parent
        self.width = self.parent.width

        mode = self.layout_mode()
        if mode == "block":
            previous = None
            for child in self.node.children:
                next = BlockLayout(child, self, previous)
                self.children.append(next)
                previous = next

        else:  # mode == "inline"
            self.cursor_x = 0
            self.cursor_y = 0
            self.weight = "normal"
            self.style = "roman"
            self.size = 12
            self.line = []

            self.recurse(self.node)
            self.flush()

        for child in self.children:
            child.layout()

        # height can only be calculated after all children are laid out
        if mode == "block":
            self.height = sum([
                child.height for child in self.children])
        else:
            self.height = self.cursor_y

    def paint(self) -> list[DrawText | DrawRect]:
        cmds = []

        bgcolor = self.node.style.get("background-color",
                                      "transparent")
        if bgcolor != "transparent":
            x2, y2 = self.x + self.width, self.y + self.height
            rect = DrawRect(self.x, self.y, x2, y2, bgcolor)
            cmds.append(rect)

        if self.layout_mode() == "inline":
            for x, y, word, font, color in self.display_list:
                cmds.append(DrawText(x, y, word, font, color))

        return cmds

    def layout_mode(self) -> Literal["inline", "block"]:
        """
        inline: basically leaf nodes, so no child elements (e.g. text) \n
        block: html block elements that contain other elements
        """
        if isinstance(self.node, Text):
            return "inline"
        elif any([isinstance(child, Element) and
                  child.tag in BLOCK_ELEMENTS
                  for child in self.node.children]):
            return "block"
        elif self.node.children:  # when there are children, but they are inline-level tags (e.g. <span>)
            return "inline"
        else:
            return "block"

    def recurse(self, node: Text | Element) -> None:
        if isinstance(node, Text):
            for word in node.text.split():
                self.word(node, word)
        else:  # node is an Element
            if node.tag == "br":
                self.flush()
            for child in node.children:
                self.recurse(child)

    def flush(self) -> None:
        if not self.line:
            return
        metrics = [font.metrics() for x, word, font, color in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent

        for rel_x, word, font, color in self.line:
            x = self.x + rel_x
            y = self.y + baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font, color))

        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent

        self.cursor_x = 0
        self.line = []

    def word(self, node: Text, word: str) -> None:
        color = node.style["color"]
        weight = node.style["font-weight"]
        style = node.style["font-style"]
        if style == "normal":
            style = "roman"
        size = int(float(node.style["font-size"][:-2]) * .75)  # convert css px to tkinter font size
        font = get_font(size, weight, style)
        w = font.measure(word)

        if self.cursor_x + w > self.width:
            self.flush()

        self.line.append((self.cursor_x, word, font, color))
        self.cursor_x += w + font.measure(" ")


def get_font(size: int, weight: Literal["normal", "bold"], style: Literal["roman", "italic"]) -> Font:
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight,
                                 slant=style)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]
