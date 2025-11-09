import tkinter as tk



# Custom Module Import
from utilities.window import makeWindow
from layoutmaker.getLayout import getLayoutData
from utilities.makeWindows import makeCanvasDict
from utilities.functionMap import getCanvasFunction



def main() -> tk.Tk:
    root, dims = makeWindow()
    canvases = makeCanvasDict(root, getLayoutData(), dims)
    root.update_idletasks()
    getCanvasFunction(canvases)


    return root

if __name__ == '__main__':
    root = main()
    root.mainloop()
    