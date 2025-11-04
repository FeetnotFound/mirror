import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import ephem #type:ignore
from datetime import datetime, date
from PIL import Image, ImageTk

from utilities.window import makeWindow
from utilities.makeWindows import makeCanvasDict
from layoutmaker.getLayout import getLayoutData



def solarDay() -> ephem.Date:  # type: ignore
    day = date(datetime.now().year, datetime.now().month, datetime.now().day)
    day = ephem.Date(day) #type:ignore
    
    return day #type:ignore

def getNewMoons(day:ephem.Date) -> tuple[ephem.Date, ephem.Date]: #type:ignore

    previous_new_moon:ephem.Date = ephem.previous_new_moon(day) # type: ignore
    next_new_moon:ephem.Date = ephem.next_new_moon(day) # type: ignore

    return previous_new_moon, next_new_moon #type:ignore

def get_phase_name(phase: float):
    phases_list:list[str] = ["New_Moon", "Waxing_Crescent", "First_Quarter", "Waxing_Gibbous", "Full_Moon", "Waning_Gibbous", "Third_Quarter", "Waning_Crescent"]
    
    if 0 <= phase < 0.05 or 0.95 <= phase <= 1.0:
        return phases_list[0]
    
    elif 0.05 <= phase < 0.22:
        return phases_list[1]
    
    elif 0.22 <= phase < 0.28:
        return phases_list[2]
    
    elif 0.28 <= phase < 0.45:
        return phases_list[3]
    
    elif 0.45 <= phase < 0.55:
        return phases_list[4]
    
    elif 0.55 <= phase < 0.72:
        return phases_list[5]
    
    elif 0.72 <= phase < 0.78:
        return phases_list[6]
    
    elif 0.78 <= phase < 0.95:
        return phases_list[7]

def getPictureName():
    day = solarDay() #type:ignore
    previous, next = getNewMoons(day) #type:ignore

    lunation = (day - previous) / (next - previous)  #type:ignore

    illumination = ephem.Moon(day).phase   #type:ignore
    illumination = f"{illumination:.2f}"

    phase = get_phase_name(lunation) #type:ignore
    
    return illumination, phase

def getPictureFile(phase:str) -> Image.Image:
    
    return Image.open(os.path.dirname(os.path.abspath(__file__)).replace("/modules", f"/assests/moonphases/{phase}.jpg"))
    
def getSizing(canvas: tk.Canvas, img:Image.Image, padding=0.1): #type:ignore

    canvasW:int = int(canvas.winfo_width())
    canvasH:int = int(canvas.winfo_height())

    paddingW:int = int(canvasW*padding)
    # paddingH:int = int(canvasH*padding)





    imgW = int(canvasH-(paddingW*3))

    z = int(canvasW/2)
    h = int((canvasH-imgW)/2)

    textSize:tuple[int,int] = (z, h)


    img = img.resize((imgW, imgW), Image.LANCZOS) #type:ignore

    tkImg = ImageTk.PhotoImage(img)

    return textSize, tkImg

def createImg(canvas: tk.Canvas, img): #type: ignore
    x_center = canvas.winfo_width() // 2
    y_center = canvas.winfo_height() // 2

    canvas.create_image(x_center, y_center, image=img, anchor="center") #type: ignore
    canvas.image = img #type:ignore



class moonphase:

    size:list[int] = [1]

    def __init__(self, canvas:tk.Canvas) -> None:
        self.canvas = canvas

    def putOnCanvas(self):
        illumination, phase = getPictureName() #type:ignore
        img = getPictureFile(phase) #type:ignore
        textSizing, img = getSizing(self.canvas, img) #type:ignore

        createImg(self.canvas, img)

        cH = self.canvas.winfo_height()


        x,y = textSizing

        self.canvas.create_text(x,(y-10), text = f"{phase.replace('_', ' ')}", anchor="center", width=(self.canvas.winfo_width()), fill="white", font = ("Helvetica", 24), justify='center',) #type:ignore

        self.canvas.create_text(x,((cH-y)+10), text = f"Illumination: {illumination}%", anchor="center", width=(self.canvas.winfo_width()), fill="white", font = ("Helvetica", 24), justify='center',)

        self.canvas.config(bg="black")


    # def updateCanvas(self):
    #     self.canvas.delete("all")
    #     moonphase(self.canvas).putOnCanvas()
    #     self.canvas.after(86400000 , self.updateCanvas)


def makemoonphase(canvas:tk.Canvas):
    moonphase(canvas).putOnCanvas()


def main() -> tk.Tk:
    root, dims = makeWindow(title="Moon Phases")
    canvases = makeCanvasDict(root, getLayoutData(), dims)
    root.update_idletasks()
    makemoonphase(canvases["moon"][0])

    return root

if __name__ == '__main__':
    root = main()
    root.mainloop()




