from tkinter import Canvas
from urllib import parse

import dukpy

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
        self.rules = None
        self.tab_height = tab_height
        self.url: URL | None = None
        self.document = None
        self.nodes = None
        self.display_list = []
        self.scroll = 0
        self.history = []
        self.focus = None

    def load(self, url: URL, payload: str | None = None) -> None:
        self.scroll = 0
        self.history.append(url)
        self.url = url
        body = url.request(payload)

        self.nodes = HTMLParser(body).parse()
        self.rules = DEFAULT_STYLE_SHEET.copy()

        links = [node.attributes["href"]
                 for node in tree_to_list(self.nodes, [])
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
            self.rules.extend(CSSParser(body).parse())

        scripts = [node.attributes["src"] for node
                   in tree_to_list(self.nodes, [])
                   if isinstance(node, Element)
                   and node.tag == "script"
                   and "src" in node.attributes]
        for script in scripts:
            script_url = url.resolve(script)
            try:
                body = script_url.request()
            except Exception:
                continue
            print("Script returned: ", dukpy.evaljs(body))

        self.render()

    def render(self):
        style(self.nodes, sorted(self.rules, key=cascade_priority))
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
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

    def keypress(self, char):
        if self.focus:
            self.focus.attributes["value"] += char
            self.render()

    def click(self, x: int, y: int) -> None:
        if self.focus:
            self.focus.is_focused = False
        self.focus = None

        y += self.scroll
        objs = [obj for obj in tree_to_list(self.document, [])
                if obj.x <= x < obj.x + obj.width
                and obj.y <= y < obj.y + obj.height]

        if not objs:
            return self.render()

        # objs is a list since the layout objects can overlap
        # i.e. a div containing a link, or a text inside a link
        # the list contains the layout objects from the back to the front
        # we then get the last one, so the one on top - the most specific one
        elt = objs[-1].node
        while elt:
            if isinstance(elt, Text):
                pass
            elif elt.tag == "a" and "href" in elt.attributes:
                url = self.url.resolve(elt.attributes["href"])
                return self.load(url)
            elif elt.tag == "input":
                self.focus = elt
                self.focus.is_focused = True
                elt.attributes["value"] = ""
                return self.render()
            elif elt.tag == "button":
                while elt:
                    if elt.tag == "form" and "action" in elt.attributes:
                        return self.submit_form(elt)
                    elt = elt.parent
            elt = elt.parent

        self.render()
        return None

    def submit_form(self, elt):
        inputs = [node for node in tree_to_list(elt, [])
                  if isinstance(node, Element)
                  and node.tag == "input"
                  and "name" in node.attributes]
        body = ""
        for input in inputs:
            name = input.attributes["name"]
            value = input.attributes.get("value", "")
            name = parse.quote(name)
            value = parse.quote(value)
            body += "&" + name + "=" + value
        body = body[1:]
        url = self.url.resolve(elt.attributes["action"])
        self.load(url, body)


def paint_tree(layout_object: DocumentLayout | BlockLayout, display_list: list) -> None:
    if layout_object.should_paint():
        display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)


def tree_to_list(tree, list):
    list.append(tree)
    for child in tree.children:
        tree_to_list(child, list)
    return list
