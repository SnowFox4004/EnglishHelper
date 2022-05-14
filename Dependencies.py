import tkinter as tk
from ttkbootstrap.constants import *


class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    # 当光标移动指定控件是显示消息
    def showtip(self, text):
        "显示提示文本"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 200
        y = y + cy + self.widget.winfo_rooty() + 30
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=LEFT,
                         background="yellow", relief=SOLID, borderwidth=1,
                         font=("仿宋", "15"))
        label.pack(side=BOTTOM)

    # 当光标移开时提示消息隐藏
    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def Create_tips(widget, text):
    tooltip = ToolTip(widget)

    def show(event):
        tooltip.showtip(text)

    def hide(event):
        tooltip.hidetip()

    widget.bind('<Enter>', show)
    widget.bind('<Leave>', hide)

    return widget


def Decreate_tips(widget):
    widget.unbind('<Enter>')
    widget.unbind('<Leave>')
