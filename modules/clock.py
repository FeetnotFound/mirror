import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
import tkinter as tk
from utilities.makeWindows import makeCanvasDict
from utilities.window import makeWindow
from layoutmaker.getLayout import getLayoutData


strf: str = "%A,\n%B %d,\n%I:%M:%S %p"

def sizeCalc(a: float, b: float) -> int:

    # size = 65 if self.canvas.winfo_width() == (self.canvas.winfo_screenwidth()*(0.3)) else 105

    # print(self.canvas.winfo_height(), self.canvas.winfo_width())
    # sizeh = abs(int((self.canvas.winfo_height()*(2.5))))
    # sizew = abs(int((self.canvas.winfo_width()*(1.25))))
    # print(sizeh, sizew) 

    return int((5/48) * b + 5)

def getXY(canvas: tk.Canvas) -> tuple[int, int]:
    return (canvas.winfo_width())//2, ((canvas.winfo_height())//2)+10

class clock():
    size:list[int] = [2,3]

    def __init__(self, canvas:tk.Canvas) -> None:
        self.canvas:tk.Canvas = canvas
    
    def makeclock(self):
        now = datetime.now()
        text = now.strftime(strf)

        x, y = getXY(self.canvas)

        size = sizeCalc(self.canvas.winfo_height(), self.canvas.winfo_width())
        clockText = self.canvas.create_text(x, y, text=text, anchor='center', width=self.canvas.winfo_screenwidth(), fill="white", font = ("Helvetica", size), justify='center',)
        
        self.canvas.configure(bg= "black")
        
        def update_clock():
            time = datetime.now()
            
            current_time = time.strftime(strf)
            
            self.canvas.itemconfig(clockText, text=current_time)
            
            self.canvas.after(1000, update_clock)
        
        update_clock()

def makeclock(canvas:tk.Canvas):
    clock(canvas).makeclock()
      

def main() -> tk.Tk:
    root, dimensions = makeWindow(title = "Clock Func")
    canvases = makeCanvasDict(root, getLayoutData(), dimensions)
    root.update_idletasks()
    clock(canvases["clock"][0]).makeclock()

    return root

if __name__ == '__main__':
    root = main()

    root.mainloop()

