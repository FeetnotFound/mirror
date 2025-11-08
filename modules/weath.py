import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from pathlib import Path
    from dotenv import load_dotenv

    # Step 1: Find the parent folder
    parent_folder = Path(__file__).resolve().parent.parent

    # Step 2: Specify the path to the .env file
    env_path = parent_folder / "variables.env"

    # Step 3: Load it
    load_dotenv(dotenv_path=env_path)
except:
    pass

from typing import Any
import requests
import math
from serpapi.google_search import GoogleSearch
import tkinter as tk 
from PIL import Image, ImageTk
from io import BytesIO
from cairosvg import svg2png #type:ignore
from datetime import datetime

from utilities.window import makeWindow
from utilities.makeWindows import makeCanvasDict
from layoutmaker.getLayout import getLayoutData

WANTEDINFO = ["temperature", "unit", "precipitation", "humidity", "wind", "location", "date", "weather"]

def get_location() -> tuple[float, float, str]:
    """Get approximate lat/lon from IP address."""
    try:
        r = requests.get("https://ipinfo.io/json")
        r.raise_for_status()
        loc = r.json()["loc"].split(",")
        lat, lon = float(loc[0]), float(loc[1])
        city = r.json().get("city", "Unknown City")
        region = r.json().get("region", "")
        return lat, lon, f"{city}, {region}"
    except Exception as e:
        print("Could not get location:", e)
        return 0.0, 0.0, "Unknown"

def getRelativeHumid(t:float, td:float) ->float:
    es = math.exp(((17.625*t)/(243.04+t)))
    ed = math.exp(((17.625*td)/(243.04+td)))

    rh = 100*(ed/es)
    return rh

def get_weather(city:str) ->dict[Any,Any]:
    params:dict[str,str] = {
        "engine": "google",
        "q": f"weather in {city}",
        "api_key": str(os.getenv("SERPAPI"))
    }

    search = GoogleSearch(params)

    searchResult:dict[Any,Any] = search.get_dict() #type:ignore

    return searchResult["answer_box"] #type:ignore

def feels_like(temp:float, wind_speed:float, humidity:float, unit:str="Celcius"):
    """
    Calculate 'feels like' temperature based on the measurement system.
    
    Parameters:
        temp: Temperature (°C if Celcius, °F if Fahrenheit)
        wind_speed: Wind speed (km/h if Celcius, mph if Fahrenheit)
        humidity: Relative humidity (%)
        unit: "Celcius" or "Fahrenheit"
    
    Returns:
        Feels-like temperature in the same unit as input
    """
    
    if unit not in ["Celcius", "Fahrenheit"]:
        raise ValueError("unit must be 'Celcius' or 'Fahrenheit'")

    # --- Wind Chill ---
    if (unit == "Fahrenheit" and temp <= 50) or (unit == "Celcius" and temp <= 10):
        if unit == "Fahrenheit":
            wc = 35.74 + 0.6215*temp - 35.75*wind_speed**0.16 + 0.4275*temp*wind_speed**0.16
        else:
            wc = 13.12 + 0.6215*temp - 11.37*wind_speed**0.16 + 0.3965*temp*wind_speed**0.16
        return round(wc, 1)

    # --- Heat Index ---
    if (unit == "Fahrenheit" and temp >= 80) or (unit == "Celcius" and temp >= 27):
        if unit == "Fahrenheit":
            # convert °C to °F
            temp_f = temp * 9/5 + 32
        else:
            temp_f = temp
        
        RH = humidity
        # Heat Index formula constants
        c1 = -42.379
        c2 = 2.04901523
        c3 = 10.14333127
        c4 = -0.22475541
        c5 = -0.00683783
        c6 = -0.05481717
        c7 = 0.00122874
        c8 = 0.00085282
        c9 = -0.00000199
        
        HI_f = (c1 + c2*temp_f + c3*RH + c4*temp_f*RH + c5*temp_f**2 +
                c6*RH**2 + c7*temp_f**2*RH + c8*temp_f*RH**2 + c9*temp_f**2*RH**2)
        
        if unit == "Celcius":
            return round((HI_f - 32) * 5/9, 1)  # convert back to °C
        else:
            return round(HI_f, 1)

    # --- Apparent Temperature (Steadman) ---
    # convert wind to m/s if necessary
    V = wind_speed / 3.6 if unit == "Celcius" else wind_speed * 0.44704
    # vapor pressure in hPa
    e = humidity / 100 * 6.105 * math.exp(17.27 * temp / (237.7 + temp))
    AT = temp + 0.33*e - 0.70*V - 4.0
    return round(AT, 1)

def parseWeather(weatherDict:dict[Any, Any] = get_weather(get_location()[-1])) ->dict[str,Any]:
    newWeatherDict:dict[str, Any] = {}
    for wantedKey in WANTEDINFO:
        newWeatherDict[wantedKey] = weatherDict[wantedKey]

    
    newWeatherDict["high"] = weatherDict["forecast"][0]["temperature"]["high"]
    newWeatherDict["low"] = weatherDict["forecast"][0]["temperature"]["low"]
    newWeatherDict["feelslike"] = feels_like(wind_speed=float(newWeatherDict["wind"].split()[0]), temp=float(newWeatherDict["temperature"]), humidity=float((int(newWeatherDict["humidity"].rstrip("%")))/100), unit=newWeatherDict["unit"])
    newWeatherDict["imgurl"] = weatherDict["hourly_forecast"][0]["thumbnail"]
    return newWeatherDict

def draw_image(img: Any, imgsize:float) -> Any:
    png_data = BytesIO()
    svg2png(
        bytestring=img,
        write_to=png_data,
        output_width=imgsize,   
        output_height=imgsize
    )
    png_data.seek(0)

    image = Image.open(png_data)
    photo = ImageTk.PhotoImage(image)

    return photo

def drawCondition(canvas:tk.Canvas, url:str, padding:int=15):
    response = (requests.get(url)).content

    width, height = (canvas.winfo_width(), canvas.winfo_height())

    x = width - (height/2)
    imgsize = height/2

    photo = draw_image(response, imgsize)


    canvas.create_image(x, 0, image=photo, anchor="nw") #type:ignore

    # Keep reference
    if not hasattr(canvas, "images"):
        canvas.images = [] #type:ignore
    canvas.images.append(photo) #type:ignore

def drawCondText(canvas:tk.Canvas, weather:dict[str,Any], padding:int = 15):

    temp, feels, cond = (weather["temperature"],weather["feelslike"],weather["weather"])

    width, height = (canvas.winfo_width(), canvas.winfo_height())

    y = height/4

    # Condtion Text

    condtextwidth = width - (height/2)



    canvas.create_text(padding,padding, text = cond, width=condtextwidth, fill= "white", anchor="nw", font=("Helvetica", 40), justify="center")



    # Feels text

    temptextWidth = condtextwidth/2

    canvas.create_text(padding, y, text=f"{feels}°", width=temptextWidth, fill= "white", anchor="nw", font=("Helvetica", 60), justify="center")


    # Temp text


    canvas.create_text(temptextWidth+(padding*2), y+(padding/2), text=f"{int(temp)}°", width=temptextWidth, fill="gray", anchor="nw", font=("Helvetica", 50), justify="center")

def drawPrecip(canvas:tk.Canvas, precipitation:str, padding:int = 15):

    _, height = (canvas.winfo_width(), canvas.winfo_height())


    imgsize = height/3
    y = height*(2/3)-(padding*2)
    ty= height*(3/4)

    imgPath = os.path.dirname(os.path.abspath(__file__)).replace("/modules", "/assests/weather_icons/showers_dark.svg")
    with open(imgPath, "rb") as f: #type:ignore
        svg_data = f.read() #type:ignore
    
    photo = draw_image(svg_data, imgsize)


    canvas.create_image(padding, y, image=photo, anchor="nw") #type:ignore
    canvas.create_text(imgsize+(padding*5), ty, text=precipitation, fill = "white", font=("Helvetica", 50), justify="center")


    
    # Keep reference
    if not hasattr(canvas, "images"):
        canvas.images = [] #type:ignore
    canvas.images.append(photo) #type:ignore

def drawWind(canvas:tk.Canvas, wind:str, padding:int = 15):

    width, height = (canvas.winfo_width(), canvas.winfo_height())

    x = width/2+padding
    imgsize = height/3
    y= height*(2/3)-(padding*2)
    ty= height*(3/4)


    imgPath = os.path.dirname(os.path.abspath(__file__)).replace("/modules", "/assests/weather_icons/windy_breezy_dark.svg")
    with open(imgPath, "rb") as f: #type:ignore
        svg_data = f.read() #type:ignore
    
    photo = draw_image(svg_data, imgsize)


    canvas.create_image(x, y, image=photo, anchor="nw") #type:ignore

    canvas.create_text(x+imgsize+(padding*4.5), ty, text=wind.replace(" ", "\n"), fill = "white", font=("Helvetica", 50), justify="center")
    # Keep reference
    if not hasattr(canvas, "images"):
        canvas.images = [] #type:ignore
    canvas.images.append(photo) #type:ignore


    

class weather:
    size:list[int] = [2,3]

    def __init__(self, canvas:tk.Canvas) -> None:
        self.canvas = canvas


    def drawWeather(self):

        weatherD = parseWeather()
        drawCondition(self.canvas, weatherD["imgurl"])
        drawCondText(self.canvas, weatherD)
        drawPrecip(self.canvas, weatherD["precipitation"])
        drawWind(self.canvas, weatherD["wind"])
        self.canvas.config(bg="black")
        

        def updateWeather():
            checker = datetime.now()
            if checker.hour in [4, 8, 12, 16, 20, 24]:
                print("update")
                self.canvas.delete("all")
                weatherD = parseWeather()
                drawCondition(self.canvas, weatherD["imgurl"])
                drawCondText(self.canvas, weatherD)
                drawPrecip(self.canvas, weatherD["precipitation"])
                drawWind(self.canvas, weatherD["wind"])

            self.canvas.after(1000,updateWeather)
            
        updateWeather()

def makeweather(canvas:tk.Canvas):
    weather(canvas).drawWeather()


def main() -> tk.Tk:
    root, dims = makeWindow(title="Weather")
    canvases = makeCanvasDict(root, getLayoutData(), dims)
    root.update_idletasks()
    makeweather(canvases["weather"][0])



    return root

if __name__ == '__main__':
    root = main()
    root.mainloop()