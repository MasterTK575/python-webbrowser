from tkinter import Canvas

from src.Rect import Rect


class DrawText:
    def __init__(self, x1, y1, text, font, color):
        self.top = y1
        self.left = x1
        self.text = text
        self.font = font
        self.bottom = y1 + font.metrics("linespace")
        self.color = color
        self.rect = Rect(self.left, self.top,
                         self.font.measure(self.text), self.bottom)

    def execute(self, scroll, canvas: Canvas):
        canvas.create_text(
            self.left, self.top - scroll,
            text=self.text,
            font=self.font,
            fill=self.color,
            anchor='nw')
