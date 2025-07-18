from src.dom.Element import Element
from src.dom.Text import Text


class HTMLParser:
    SELF_CLOSING_TAGS = [
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    ]
    HEAD_TAGS = [
        "base", "basefont", "bgsound", "noscript",
        "link", "meta", "title", "style", "script",
    ]

    def __init__(self, body: str):
        self.body = body
        self.unfinished = []

    def parse(self) -> Element:
        token = ""
        in_tag = False
        for c in self.body:
            if c == "<":
                in_tag = True
                if token:
                    self.add_text(token)  # empty text not possible
                token = ""
            elif c == ">":
                in_tag = False
                self.add_tag(token)  # empty tag is possible
                token = ""
            else:
                token += c
        if not in_tag and token:
            self.add_text(token)  # dump any remaining text
        return self.finish()  # we handle missing closing tags, but not unfinished tags!

    def add_text(self, text: str) -> None:
        if text.isspace():
            return
        self.implicit_tags(None)
        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)  # text elements are directly finished

    def add_tag(self, tag: str) -> None:
        tag, attributes = self.get_attributes(tag)
        if tag.startswith("!"):  # ignore comments and doctype (<!DOCTYPE html>)
            return
        self.implicit_tags(tag)
        if tag.startswith("/"):
            if len(self.unfinished) == 1:
                return  # in case of root element just skip
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)  # only finished tags are added to children

        elif tag in self.SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]
            node = Element(tag, attributes, parent)
            parent.children.append(node)

        else:
            parent = self.unfinished[-1] if self.unfinished else None
            node = Element(tag, attributes, parent)
            self.unfinished.append(node)

    def finish(self) -> Element:
        if not self.unfinished:
            self.implicit_tags(None)
        while len(self.unfinished) > 1:  # handle missing closing tags
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        return self.unfinished.pop()  # return root html element

    def implicit_tags(self, tag: str | None) -> None:
        while True:
            open_tags = [node.tag for node in self.unfinished]
            if open_tags == [] and tag != "html":
                self.add_tag("html")
            elif (open_tags == ["html"] and
                  tag not in ["head", "body", "/html"]):
                if tag in self.HEAD_TAGS:
                    self.add_tag("head")
                else:
                    self.add_tag("body")
            elif (open_tags == ["html", "head"] and
                  tag not in ["/head"] + self.HEAD_TAGS):
                self.add_tag("/head")
            else:
                break

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
