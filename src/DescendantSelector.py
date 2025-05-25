from __future__ import annotations

from src.Element import Element
from src.TagSelector import TagSelector
from src.Text import Text


class DescendantSelector:
    def __init__(self, ancestor: DescendantSelector | TagSelector,
                 descendant: TagSelector):
        self.ancestor = ancestor
        self.descendant = descendant
        self.priority = ancestor.priority + descendant.priority

    def matches(self, node: Element | Text) -> bool:
        if not self.descendant.matches(node):
            return False
        while node.parent:
            if self.ancestor.matches(node.parent):
                return True
            node = node.parent
        return False
