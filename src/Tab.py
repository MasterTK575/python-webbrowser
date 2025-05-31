from tkinter import Canvas

from src.CSSParser import CSSParser, cascade_priority, style
from src.Constants import *
from src.Element import Element
from src.HTMLParser import HTMLParser
from src.Text import Text
from src.URL import URL
from src.layout.BlockLayout import BlockLayout
from src.layout.DocumentLayout import DocumentLayout

DEFAULT_STYLE_SHEET = CSSParser(open("browser.css").read()).parse()


class Tab:
    def __init__(self, tab_height) -> None:
        self.tab_height = tab_height
        self.url: URL | None = None
        self.document = None
        self.root = None
        self.display_list = []
        self.scroll = 0
        self.history = []

    def load(self, url: URL) -> None:
        self.history.append(url)
        self.url = url
        body = url.request()

        self.root = HTMLParser(body).parse()
        rules = DEFAULT_STYLE_SHEET.copy()

        links = [node.attributes["href"]
                 for node in tree_to_list(self.root, [])
                 if isinstance(node, Element)
                 and node.tag == "link"
                 and node.attributes.get("rel") == "stylesheet"
                 and "href" in node.attributes]

        for link in links:
            style_url = url.resolve(link)
            try:
                body = style_url.request()
            except Exception:
                continue
            rules.extend(CSSParser(body).parse())

        style(self.root, sorted(rules, key=cascade_priority))

        self.document = DocumentLayout(self.root)
        self.document.layout()

        self.display_list = []  # reset display list to remove old elements when loading a new page
        paint_tree(self.document, self.display_list)

    def go_back(self):
        if len(self.history) > 1:
            self.history.pop()  # remove current page
            back = self.history.pop()
            self.load(back)

    def draw(self, canvas: Canvas, offset):
        for cmd in self.display_list:
            if cmd.rect.top > self.scroll + self.tab_height:
                continue
            if cmd.rect.bottom < self.scroll:
                continue
            cmd.execute(self.scroll - offset, canvas)

    def scrolldown(self):
        max_y = max(self.document.height + 2 * VSTEP - self.tab_height, 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)

    def scrollup(self):
        self.scroll -= SCROLL_STEP

    def click(self, x: int, y: int) -> None:
        # x and y: screen coordinates
        y += self.scroll  # page coordinates (account for scroll)

        # meaning element can't be on the right of the click
        # and also starting pos + width has to overlap the click position
        objs = [obj for obj in tree_to_list(self.document, [])
                if obj.x <= x < obj.x + obj.width
                and obj.y <= y < obj.y + obj.height]  # get layout objects

        if not objs:
            return None

        elt = objs[-1].node  # get most specific element
        while elt:
            if isinstance(elt, Text):
                pass
            elif elt.tag == "a" and "href" in elt.attributes:
                url = self.url.resolve(elt.attributes["href"])
                return self.load(url)
            elt = elt.parent

        return None


def paint_tree(layout_object: DocumentLayout | BlockLayout, display_list: list) -> None:
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)


def tree_to_list(tree, list):
    list.append(tree)
    for child in tree.children:
        tree_to_list(child, list)
    return list
