from __future__ import annotations

from typing import Literal

from src.DrawRect import DrawRect
from src.Element import Element
from src.Rect import Rect
from src.Text import Text
from src.layout.Fonts import get_font
from src.layout.LineLayout import LineLayout
from src.layout.TextLayout import TextLayout

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

        self.width = None
        self.x = None
        self.y = None
        self.cursor_x = None
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
            self.new_line()
            self.recurse(self.node)

        for child in self.children:
            child.layout()

        # height is now height of all children elements (including line layouts)
        self.height = sum([child.height for child in self.children])

    def paint(self) -> list[DrawRect]:
        cmds = []
        bgcolor = self.node.style.get("background-color",
                                      "transparent")
        if bgcolor != "transparent":
            rect = DrawRect(self.self_rect(), bgcolor)
            cmds.append(rect)

        return cmds

    def layout_mode(self) -> Literal["inline", "block"]:
        """
        inline: basically leaf nodes, so no child elements (e.g. text)

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
                self.new_line()
            for child in node.children:
                self.recurse(child)

    def word(self, node: Text, word: str) -> None:
        weight = node.style["font-weight"]
        style = node.style["font-style"]
        if style == "normal":
            style = "roman"
        size = int(float(node.style["font-size"][:-2]) * .75)  # convert css px to tkinter font size
        font = get_font(size, weight, style)
        w = font.measure(word)

        if self.cursor_x + w > self.width:
            self.new_line()
        self.cursor_x += w + font.measure(" ")

        line = self.children[-1]
        previous_word = line.children[-1] if line.children else None
        text = TextLayout(node, word, line, previous_word)
        line.children.append(text)

    def new_line(self):
        self.cursor_x = 0
        last_line = self.children[-1] if self.children else None
        new_line = LineLayout(self.node, self, last_line)
        self.children.append(new_line)

    def self_rect(self) -> Rect:
        return Rect(self.x, self.y,
                    self.x + self.width, self.y + self.height)
