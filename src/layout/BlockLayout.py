from __future__ import annotations

from typing import Literal

from src.Constants import INPUT_WIDTH_PX
from src.DrawRect import DrawRect
from src.Element import Element
from src.Rect import Rect
from src.Text import Text
from src.layout.Fonts import get_font
from src.layout.InputLayout import InputLayout
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
        if isinstance(self.node, Text):
            return "inline"
        elif any([isinstance(child, Element) and
                  child.tag in BLOCK_ELEMENTS
                  for child in self.node.children]):
            return "block"
        # why children? because <p>This is some text.</p> would have a Text("This is some text.") child node
        elif self.node.children or self.node.tag == "input":
            return "inline"
        else:  # fallback - any self-closing tag or empty element (e.g. <div></div>)
            return "block"

    def recurse(self, node: Text | Element) -> None:
        if isinstance(node, Text):
            for word in node.text.split():
                self.word(node, word)
        else:  # node is an Element
            if node.tag == "br":
                self.new_line()
            elif node.tag == "input" or node.tag == "button":
                self.input(node)
            else:
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

    def input(self, node):
        w = INPUT_WIDTH_PX
        if self.cursor_x + w > self.width:
            self.new_line()
        line = self.children[-1]
        previous_word = line.children[-1] if line.children else None
        input = InputLayout(node, line, previous_word)
        line.children.append(input)

        weight = node.style["font-weight"]
        style = node.style["font-style"]
        if style == "normal":
            style = "roman"
        size = int(float(node.style["font-size"][:-2]) * .75)
        font = get_font(size, weight, style)

        self.cursor_x += w + font.measure(" ")

    def should_paint(self):
        return isinstance(self.node, Text) or \
            (self.node.tag != "input" and self.node.tag != "button")

    def new_line(self):
        self.cursor_x = 0
        last_line = self.children[-1] if self.children else None
        new_line = LineLayout(self.node, self, last_line)
        self.children.append(new_line)

    def self_rect(self) -> Rect:
        return Rect(self.x, self.y,
                    self.x + self.width, self.y + self.height)
