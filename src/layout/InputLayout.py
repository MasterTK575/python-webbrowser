from src.dom.Text import Text
from src.drawing.DrawLine import DrawLine
from src.drawing.DrawRect import DrawRect
from src.drawing.DrawText import DrawText
from src.layout.Rect import Rect
from src.styling.Fonts import get_font
from src.user_agent.Constants import INPUT_WIDTH_PX


class InputLayout:
    def __init__(self, node, parent, previous):
        self.y = None
        self.x = None
        self.height = None
        self.width = None
        self.font = None
        self.node = node
        self.children = []
        self.parent = parent
        self.previous = previous

    def layout(self):
        weight = self.node.style["font-weight"]
        style = self.node.style["font-style"]
        if style == "normal":
            style = "roman"
        size = int(float(self.node.style["font-size"][:-2]) * .75)
        self.font = get_font(size, weight, style)

        self.width = INPUT_WIDTH_PX

        if self.previous:
            space = self.previous.font.measure(" ")
            self.x = self.previous.x + space + self.previous.width
        else:
            self.x = self.parent.x

        self.height = self.font.metrics("linespace")

    def paint(self):
        cmds = []
        bgcolor = self.node.style.get("background-color",
                                      "transparent")
        if bgcolor != "transparent":
            rect = DrawRect(self.self_rect(), bgcolor)
            cmds.append(rect)

        text = ""
        if self.node.tag == "input":
            text = self.node.attributes.get("value", "")
        elif self.node.tag == "button":
            if len(self.node.children) == 1 and \
                    isinstance(self.node.children[0], Text):
                text = self.node.children[0].text
            else:
                print("Ignoring HTML contents inside button")
                text = ""

        color = self.node.style["color"]
        cmds.append(
            DrawText(self.x, self.y, text, self.font, color))

        if self.node.is_focused:
            cx = self.x + self.font.measure(text)
            cmds.append(DrawLine(
                cx, self.y, cx, self.y + self.height, "black", 1))

        return cmds

    def self_rect(self) -> Rect:
        return Rect(self.x, self.y,
                    self.x + self.width, self.y + self.height)

    def should_paint(self) -> bool:
        return True
