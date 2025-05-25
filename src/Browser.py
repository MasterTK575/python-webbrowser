import tkinter
import tkinter.font

from src.BlockLayout import BlockLayout
from src.Constants import *
from src.DocumentLayout import DocumentLayout
from src.HTMLParser import HTMLParser, print_tree
from src.URL import URL


class Browser:
    def __init__(self) -> None:
        self.document = None
        self.nodes = None
        self.display_list = []
        self.scroll = 0
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()

        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)

    def load(self, url: URL) -> None:
        body = url.request()
        self.nodes = HTMLParser(body).parse()
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        paint_tree(self.document, self.display_list)
        self.draw()

        # for debugging purposes
        print_tree(self.nodes)
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


if __name__ == "__main__":
    import sys

    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
