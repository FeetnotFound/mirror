# https://github.com/mikebrady/shairport-sync/

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


try:
    from pathlib import Path
    from dotenv import load_dotenv


    # Step 1: Find the parent folder
    parent_folder = Path(__file__).resolve().parent.parent


    # Step 2: Specify the path to the .env file
    env_path = parent_folder / 'variables.env'


    # Step 3: Load it
    load_dotenv(dotenv_path=env_path)
except:
    pass

                                                              
from typing import Optional, Dict, Any
import paho.mqtt.client as mqtt

import warnings
from PIL import Image, ImageTk #type:ignore
import tkinter as tk

warnings.filterwarnings("ignore", category=DeprecationWarning)

from utilities.window import makeWindow
from utilities.makeWindows import makeCanvasDict
from layoutmaker.getLayout import getLayoutData



# --- Configuration ---
MQTT_BROKER: str = "localhost"
MQTT_PORT: int = 1883
MQTT_TOPIC: str = "#"  # listen to all topics
MQTT_USERNAME: Optional[str] = None
MQTT_PASSWORD: Optional[str] = None

# --- Shared dictionary to store latest metadata ---
LATEST_METADATA: Dict[str, Any] = {}


# --- MQTT callbacks ---
def on_connect(client: mqtt.Client, userdata: Optional[object], flags: dict[Any, Any], rc: int) -> None:
    if rc == 0:
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"❌ MQTT connection failed with code {rc}")


def on_message(client: mqtt.Client, userdata: Optional[object], msg: mqtt.MQTTMessage) -> None:
    topic = msg.topic.lower()
    payload_bytes = msg.payload

    key = topic.split("/")[-1]

    LATEST_METADATA[key] = payload_bytes.decode("utf-8", errors="ignore")
# --- Start background listener ---
def start_mqtt_listener() -> mqtt.Client:
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()  # background thread
    return client

# --- Function to get the latest metadata ---
def get_latest_metadata() -> Dict[str, Any]:
    """
    Returns a copy of the latest metadata collected so far.
    Empty dict if nothing has arrived yet.
    """
    return LATEST_METADATA.copy()


# Start the background listener once
start_mqtt_listener()

def getMusicImg(canvas: tk.Canvas, size:int, padding:int= 15) -> tuple[int, int]:
    PATH = "/tmp/shairport-sync/.cache/coverart"
    
    valid_exts:tuple[str, str] = (".jpg", ".jpeg")

    for f in os.listdir(PATH):
        if f.lower().endswith(valid_exts):
            img_path:str = os.path.join(PATH, f)
            break

    img = Image.open(img_path) #type:ignore


    width, height = (canvas.winfo_width(), canvas.winfo_height())

    imgwidth = int(width/2)

    if size == 1:
        y = padding
    else:
        y = int((height-imgwidth)/2)

    if img:
        resized = img.resize((imgwidth, imgwidth), Image.LANCZOS)  #type:ignore 
        photo = ImageTk.PhotoImage(resized)

        canvas.create_image(padding, y, image=photo, anchor="nw") #type:ignore
                # Keep reference alive
        if not hasattr(canvas, "_photo_refs"):
            canvas._photo_refs = []  #type:ignore
        canvas._photo_refs.append(photo)  #type:ignore

        print("yuppers")
    else:
        img = Image.open(os.path.dirname(os.path.abspath(__file__)).replace("/modules", "/assests/music/no_music.png"))
        resized = img.resize((imgwidth, y), Image.LANCZOS)  #type:ignore 

        photo = ImageTk.PhotoImage(resized)

        canvas.create_image(padding, padding, image=photo, anchor="nw") #type:ignore
                # Keep reference alive
        if not hasattr(canvas, "_photo_refs"):
            canvas._photo_refs = []  #type:ignore
        canvas._photo_refs.append(photo)  #type:ignore
    return imgwidth, y

def getSize(canvas:tk.Canvas):
    root = canvas.winfo_toplevel()
    width = root.winfo_width()
    sizes:dict[int, tuple[float, float]] = {
    1: (1/3, 0.2),
    2: (1/3, 0.3),
    3: (0.4, 0.5),
}
    if width*sizes[1][1] == canvas.winfo_width():
        return 1
    else:
        return 2
    
def getTitle(canvas:tk.Canvas, size:int, picturesize:int, title:str, padding:int=15):
    width, height = (canvas.winfo_width(), canvas.winfo_height())

    
    x:int = int((padding*2)+picturesize)
    if size == 1:
        y = padding
        font = 20
    else:
        y = int((height-picturesize)/2)
        font = 30
    twidth = width-x

    canvas.create_text(x, y, text=title, width=twidth, fill="white", font=("Helvetica", font), anchor="nw")

def getArtist(canvas:tk.Canvas, size:int, picturesize:int, title:str, padding:int=15):
    width, height = (canvas.winfo_width(), canvas.winfo_height())

    
    
    if size == 1:
        y = int((height/2)+padding)
        x = padding
        font:int = 20
    else:
        y = int((height-picturesize)/2)+(picturesize*(1/3))
        x:int = int((padding*2)+picturesize)
        font = 30

    twidth = width-x

    canvas.create_text(x, y, text=title, width=twidth, fill="white", font=("Helvetica", font), anchor="nw")

def getAlbum(canvas:tk.Canvas, size:int, picturesize:int, title:str, padding:int=15):
    width, height = (canvas.winfo_width(), canvas.winfo_height())

    if size == 1:
        y = int(((height/2)+padding)+(height*(1/4)))
        x = padding
        font:int = 20
    else:
        y = int((height-picturesize)/2)+(picturesize*(2/3))
        x:int = int((padding*2)+picturesize)
        font = 30

    twidth = width-x

    canvas.create_text(x, y, text=title, width=twidth, fill="white", font=("Helvetica", font), anchor="nw")

def makemusic(canvas:tk.Canvas):

    size = getSize(canvas)

    picsize, _ = getMusicImg(canvas, size)


    metadata:dict[Any, Any] = get_latest_metadata()
    if metadata:
        print(metadata["album"], metadata["artist"], metadata["title"])
        getTitle(canvas,size, picsize, metadata["title"])
        getArtist(canvas,size, picsize, metadata["artist"])
        getAlbum(canvas,size, picsize, metadata["album"])
    else:
        pass
    
    canvas.config(bg="black")
    def updatemusic(metadata:dict[Any,Any]):
        new_metadata = get_latest_metadata()
        if new_metadata and new_metadata != metadata:
            canvas.delete("all")
            print(new_metadata.get("album"), new_metadata.get("artist"), new_metadata.get("title"))
            getMusicImg(canvas, size)
            getTitle(canvas, size, picsize, new_metadata["title"])
            getArtist(canvas,size, picsize, new_metadata["artist"])
            getAlbum(canvas,size, picsize, new_metadata["album"])
            metadata = new_metadata
        else:
            print("No update yet")
        canvas.after(1000, updatemusic, metadata)

    updatemusic(metadata)


def main() -> tk.Tk:
    root, dims = makeWindow(title = "music")
    canvases = makeCanvasDict(root, getLayoutData(), dims)
    root.update_idletasks()
    makemusic(canvases["music"][0])

    return root


if __name__ == '__main__':
    root = main()

    root.mainloop()