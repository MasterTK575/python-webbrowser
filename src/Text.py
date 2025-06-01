from src.Element import Element


class Text:
    def __init__(self, text: str, parent: Element) -> None:
        self.text = text
        self.children = []
        self.parent = parent
        self.style = {}
        self.is_focused = False

    def __repr__(self):
        return repr(self.text)
