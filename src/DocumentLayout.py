from src.BlockLayout import BlockLayout
from src.Constants import *
from src.Element import Element


class DocumentLayout:
    def __init__(self, node: Element):
        self.node = node
        self.parent = None
        self.children = []

        self.x = None
        self.y = None
        self.width = None
        self.height = None

    def layout(self) -> None:
        self.width = WIDTH - 2 * HSTEP
        self.x = HSTEP
        self.y = VSTEP

        child = BlockLayout(self.node, self, None)
        self.children.append(child)
        child.layout()

        self.height = child.height

    def paint(self) -> list:
        return []
