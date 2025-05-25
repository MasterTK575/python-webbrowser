from __future__ import annotations


class Element:
    def __init__(self, tag: str, attributes: dict[str, str], parent: Element | None) -> None:
        self.tag = tag
        self.attributes = attributes
        self.children = []
        self.parent = parent

        self.style = {}

    def __repr__(self):
        return "<" + self.tag + ">"
