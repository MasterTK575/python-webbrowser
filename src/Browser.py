import tkinter
import tkinter.font

from src.BlockLayout import BlockLayout
from src.CSSParser import CSSParser, cascade_priority, style
from src.Constants import *
from src.DocumentLayout import DocumentLayout
from src.Element import Element
from src.HTMLParser import HTMLParser, print_tree
from src.URL import URL

DEFAULT_STYLE_SHEET = CSSParser(open("browser.css").read()).parse()


class Browser:
    def __init__(self) -> None:
        self.document = None
        self.root = None
        self.display_list = []
        self.scroll = 0
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT,
            bg="white"
        )
        self.canvas.pack()

        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)

    def load(self, url: URL) -> None:
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

        paint_tree(self.document, self.display_list)
        self.draw()

        # for debugging purposes
        print_tree(self.root)
        print_tree(self.document)

    def draw(self) -> None:
        self.canvas.delete("all")
        for cmd in self.display_list:
            if cmd.top > self.scroll + HEIGHT:
                continue
            if cmd.bottom < self.scroll:
                continue
            cmd.execute(self.scroll, self.canvas)

    def scrolldown(self, e):
        max_y = max(self.document.height + 2 * VSTEP - HEIGHT, 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)
        self.draw()

    def scrollup(self, e):
        self.scroll -= SCROLL_STEP
        self.draw()


def paint_tree(layout_object: DocumentLayout | BlockLayout, display_list: list) -> None:
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)


def tree_to_list(tree, list):
    list.append(tree)
    for child in tree.children:
        tree_to_list(child, list)
    return list


if __name__ == "__main__":
    import sys

    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
