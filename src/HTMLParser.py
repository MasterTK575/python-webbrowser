from src.Element import Element
from src.Text import Text

SELF_CLOSING_TAGS = [
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
]


class HTMLParser:
    def __init__(self, body):
        self.body = body
        self.unfinished = []

    def parse(self):
        text = ""
        in_tag = False
        for c in self.body:
            if c == "<":
                in_tag = True
                if text:
                    self.add_text(text)
                text = ""
            elif c == ">":
                in_tag = False
                self.add_tag(text)
                text = ""
            else:
                text += c
        if not in_tag and text:
            self.add_text(text)
        return self.finish()

    def add_text(self, text: str):
        if text.isspace():
            return
        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)  # text elements are directly finished

    def add_tag(self, tag: str):
        tag, attributes = self.get_attributes(tag)
        if tag.startswith("!"):  # ignore comments and doctype (<!DOCTYPE html>)
            return
        if tag.startswith("/"):
            if len(self.unfinished) == 1:
                return  # in case of root element just skip
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)  # only finished tags are added to children

        elif tag in SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]
            node = Element(tag, attributes, parent)
            parent.children.append(node)

        else:
            parent = self.unfinished[-1] if self.unfinished else None
            node = Element(tag, attributes, parent)
            self.unfinished.append(node)

    def finish(self):
        while len(self.unfinished) > 1:  # handle missing closing tags
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        return self.unfinished.pop()  # return root html element

    def get_attributes(self, text: str) -> tuple[str, dict[str, str]]:
        parts = text.split()
        tag = parts[0].casefold()
        attributes = {}
        for attrpair in parts[1:]:
            if "=" in attrpair:  # when key value pair, e.g. <input type="text">
                key, value = attrpair.split("=", 1)
                if len(value) > 2 and value[0] in ["'", "\""]:  # when value is quoted
                    value = value[1:-1]
                attributes[key.casefold()] = value
            else:
                attributes[attrpair.casefold()] = ""  # when no value is given, e.g. <input disabled>
        return tag, attributes


def print_tree(node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)
