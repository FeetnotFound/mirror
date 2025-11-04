import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))




from typing import Callable, Any #type: ignore
import tkinter as tk #type: ignore


from modules.clock import makeClock, clock
from modules.moon import makemoonphase, moonphase
from modules.calend import makecalendar, calendar


function_map: dict[str, tuple[Callable[[tk.Canvas], None], list[int]]] = {
    "clock": (makeClock, clock.size),
    "moon": (makemoonphase, moonphase.size),
    "calendar": (makecalendar, calendar.size),
    }


def getCanvasFunction(canvases: dict[str, tuple[tk.Canvas, int,str]], func_map:dict[str, tuple[Callable[[tk.Canvas], None], list[int]]] = function_map):
    for name, canvasl in canvases.items():
        canvas, size, funct = canvasl
        try:
            func, size_check = func_map[funct]
            if size in size_check:
                pass
            else:
                print(name, "wrong size")
                continue
            func(canvas)
        except:
            print("nope")
