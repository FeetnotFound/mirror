import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



from utilities.window import makeWindow
from layoutmaker.getLayout import getLayoutData
import tkinter as tk
from typing import Any



sizes:dict[int, tuple[float, float]] = {
    1: (1/3, 0.2),
    2: (1/3, 0.3),
    3: (0.4, 0.5),
    4: (0.6, 0.5)
}




def getSize(category:int, dims: tuple[int, int],chart:dict[int, tuple[float, float]] = sizes) -> tuple[int, int]:
    size:tuple[float, float] = chart[category]
    x, y = dims
    h, w = size

    hp = h*x
    wp = w*y
    return (int(wp), int(hp))

def getData(data:dict[str, Any], dims: tuple[int, int]) -> tuple[bool, dict[str, Any]]:
    orienttation:bool = data["orienttation"]
    try:
        layout = data["carousel"]
    except:
        
        del data["layout"]["name"]
        layout = data["layout"]


    return orienttation, layout

def makeCanvas(window: tk.Tk, w: int, h:int, bg:str, x: int, y:int) -> tk.Canvas:
    
    Canvas = tk.Canvas(master=window, width=w, height=h, bg=bg, borderwidth=0, highlightthickness=0)
    Canvas.place(x=x, y=y, anchor='nw')
    return Canvas

def makeCanvasDict(window: tk.Tk, data: dict[str, Any], dims: tuple[int, int], canvases: dict[str, tuple[tk.Canvas, int,str]] = {}) -> dict[str, tuple[tk.Canvas, int,str]]:
    _, data = getData(data, dims)
    canvases.clear()
    my,mx = dims
    #print(my,mx)
    x:int = 1 
    for name, canvas in data.items():
        namer, x,y,size,color = canvas.values()
        size:tuple[int, int] = getSize(canvas['size'], dims)
        w, h = size

        #print(size,x,y)
        
        if x+w > mx:
            print(f"{name}, nope: x")
           
        elif y+h > my:
            print(f"{name}, nope: y")


        canvases[name] = (makeCanvas(window, w, h, color, x, y), canvas['size'], namer)
        
    return canvases



def main() -> None:
    window, dims = makeWindow(title="makeWindows")
    makeCanvasDict(window, getLayoutData(), dims)


    window.mainloop()


if __name__ == "__main__":
    main()
