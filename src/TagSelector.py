from src.Element import Element
from src.Text import Text


class TagSelector:
    def __init__(self, tag: str):
        self.tag = tag
        self.priority = 1

    def matches(self, node: Element | Text) -> bool:
        return isinstance(node, Element) and self.tag == node.tag
