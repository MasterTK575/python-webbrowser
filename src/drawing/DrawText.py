from tkinter import Canvas

from src.layout.Rect import Rect


class DrawText:
    def __init__(self, x1, y1, text, font, color):
        self.top = y1
        self.left = x1
        self.text = text
        self.font = font
        self.bottom = y1 + font.metrics("linespace")
        self.color = color
        self.rect = Rect(x1, y1,
                         x1 + font.measure(text), self.bottom)

    def execute(self, scroll, canvas: Canvas):
        canvas.create_text(
            self.left, self.top - scroll,
            text=self.text,
            font=self.font,
            fill=self.color,
            anchor='nw')
