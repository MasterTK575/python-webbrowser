import tkinter
import tkinter.font

from src.HTMLParser import HTMLParser, print_tree
from src.Layout import Layout
from src.URL import URL

WIDTH, HEIGHT = 800, 600
HORIZONTAL_STEP, VERTICAL_STEP = 13, 18
SCROLL_STEP = 100


class Browser:
    def __init__(self) -> None:
        self.nodes = None
        self.display_list = None
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
        self.display_list = Layout(self.nodes).display_list
        print_tree(self.nodes)
        self.draw()

    def draw(self) -> None:
        self.canvas.delete("all")
        for x, y, word, font in self.display_list:
            if y > self.scroll + HEIGHT:
                continue
            if y + VERTICAL_STEP < self.scroll:
                continue
            self.canvas.create_text(x, y - self.scroll, text=word, font=font, anchor='nw')

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def scrollup(self, e):
        self.scroll -= SCROLL_STEP
        self.draw()


if __name__ == "__main__":
    import sys

    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
