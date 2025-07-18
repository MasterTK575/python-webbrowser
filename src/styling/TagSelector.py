from src.dom.Element import Element
from src.dom.Text import Text


class TagSelector:
    def __init__(self, tag: str):
        self.tag = tag
        self.priority = 1

    def matches(self, node: Element | Text) -> bool:
        # Text Element hat ja keinen Tag
        return isinstance(node, Element) and self.tag == node.tag
