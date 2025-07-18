from __future__ import annotations

from src.dom.Element import Element
from src.dom.Text import Text
from src.styling.TagSelector import TagSelector


class DescendantSelector:
    def __init__(self, ancestor: DescendantSelector | TagSelector,
                 descendant: TagSelector):
        self.ancestor = ancestor
        self.descendant = descendant
        self.priority = ancestor.priority + descendant.priority

    def matches(self, node: Element | Text) -> bool:
        if not self.descendant.matches(node):
            return False

        # Laufe so lange nach oben, bis man passenden Vorfahren findet
        while node.parent:
            if self.ancestor.matches(node.parent):
                return True
            node = node.parent
        return False
