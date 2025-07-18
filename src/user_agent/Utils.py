from src.layout.BlockLayout import BlockLayout
from src.layout.DocumentLayout import DocumentLayout
from src.layout.InputLayout import InputLayout
from src.layout.LineLayout import LineLayout
from src.layout.TextLayout import TextLayout


def paint_tree(layout_object: DocumentLayout | BlockLayout | LineLayout | TextLayout | InputLayout,
               display_list: list) -> None:
    if layout_object.should_paint():
        display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)


def tree_to_list(tree, list):
    list.append(tree)
    for child in tree.children:
        tree_to_list(child, list)
    return list
