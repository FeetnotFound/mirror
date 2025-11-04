import tkinter as tk



def makeWindow(dimensions: tuple[int,int] = (0,0), title:str = "Smart Mirror", fullscreen: bool = True) -> tuple[tk.Tk, tuple[int,int]]:
    window: tk.Tk = tk.Tk()
    window.configure(bg="black")
    if fullscreen:
        window.attributes("-fullscreen", True) #type: ignore
        dimensions = (window.winfo_screenheight(), window.winfo_screenwidth())
    else:
        window.geometry(f"{dimensions[0]}x{dimensions[-1]}")
    window.title(title)

    def closeWin(event):  # type: ignore
        window.destroy()
    
    window.bind("<Escape>", closeWin) #type: ignore

    return window, dimensions

def main() -> None:
    window, dimensions = makeWindow((900,900))

    print(dimensions)

    window.mainloop()

if __name__ == '__main__':
    main()