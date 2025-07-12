from tkinter import Canvas
from urllib import parse

from src.CSSParser import CSSParser, cascade_priority, style
from src.Constants import *
from src.Element import Element
from src.HTMLParser import HTMLParser
from src.JSContext import JSContext
from src.Text import Text
from src.URL import URL
from src.Utils import tree_to_list, paint_tree
from src.layout.DocumentLayout import DocumentLayout

DEFAULT_STYLE_SHEET = CSSParser(open("browser.css").read()).parse()


class Tab:
    def __init__(self, tab_height) -> None:
        self.allowed_origins = None
        self.js = None
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
        headers, body = url.request(self.url, payload)
        self.url = url  # has to be set after request

        self.nodes = HTMLParser(body).parse()
        self.rules = DEFAULT_STYLE_SHEET.copy()

        self.allowed_origins = None
        if "content-security-policy" in headers:
            csp = headers["content-security-policy"].split()
            if len(csp) > 0 and csp[0] == "default-src":
                self.allowed_origins = []
                for origin in csp[1:]:
                    self.allowed_origins.append(URL(origin).origin())

        links = [node.attributes["href"]
                 for node in tree_to_list(self.nodes, [])
                 if isinstance(node, Element)
                 and node.tag == "link"
                 and node.attributes.get("rel") == "stylesheet"
                 and "href" in node.attributes]
        for link in links:
            style_url = url.resolve(link)
            if not self.allowed_request(style_url):
                print("Blocked stylesheet", link, "due to CSP")
                continue
            try:
                header, body = style_url.request(url)
            except Exception:
                continue
            self.rules.extend(CSSParser(body).parse())

        scripts = [node.attributes["src"] for node
                   in tree_to_list(self.nodes, [])
                   if isinstance(node, Element)
                   and node.tag == "script"
                   and "src" in node.attributes]
        self.js = JSContext(self)
        for script in scripts:
            script_url = url.resolve(script)
            if not self.allowed_request(script_url):
                print("Blocked script", script, "due to CSP")
                continue
            try:
                header, body = script_url.request(url)
            except Exception:
                continue
            self.js.run(script, body)

        self.render()

    def allowed_request(self, url):
        return self.allowed_origins is None or \
            url.origin() in self.allowed_origins

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
            if self.js.dispatch_event("keydown", self.focus):
                return

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
                if self.js.dispatch_event("click", elt):
                    return None

                url = self.url.resolve(elt.attributes["href"])
                return self.load(url)
            elif elt.tag == "input":
                if self.js.dispatch_event("click", elt):
                    return None

                self.focus = elt
                self.focus.is_focused = True
                elt.attributes["value"] = ""
                return self.render()
            elif elt.tag == "button":
                if self.js.dispatch_event("click", elt):
                    return None

                while elt:
                    if elt.tag == "form" and "action" in elt.attributes:
                        return self.submit_form(elt)
                    elt = elt.parent
            elt = elt.parent

        self.render()
        return None

    def submit_form(self, elt):
        if self.js.dispatch_event("submit", elt):
            return

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
