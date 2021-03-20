# Try importing Tk for clipboard support
try:
    from tkinter import Tk
except ImportError:
    Tk = None


def copy_to_clipboard(string: str):
    """Copies a string to clipboard using Tk"""
    if Tk is not None:
        r = Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(string)
        r.update()
        r.destroy()
