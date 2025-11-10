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
        y = 0
        x = int((width-imgwidth)/2)
    else:
        y = int((height-imgwidth)/2)
        x = padding

    if img:
        resized = img.resize((imgwidth, imgwidth), Image.LANCZOS)  #type:ignore 
        photo = ImageTk.PhotoImage(resized)

        canvas.create_image(x, y, image=photo, anchor="nw") #type:ignore
                # Keep reference alive
        if not hasattr(canvas, "_photo_refs"):
            canvas._photo_refs = []  #type:ignore
        canvas._photo_refs.append(photo)  #type:ignore

        print("yuppers")
    else:
        img = Image.open(os.path.dirname(os.path.abspath(__file__)).replace("/modules", "/assests/music/no_music.png"))
        resized = img.resize((imgwidth, y), Image.LANCZOS)  #type:ignore 

        photo = ImageTk.PhotoImage(resized)

        canvas.create_image(x, padding, image=photo, anchor="nw") #type:ignore
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
    
def getTitle(canvas:tk.Canvas, size:int, picturesize:int, title:Any, Artist:Any, Album: Any, padding:int=15):
    if title:
        pass
    else:
        title = "No Song Title"
    if Artist:
        pass
    else:
        Artist = "No Song Artist"
    if Album:
        pass
    else:
        Album = "No Song Artist"
    theText = f"{title}\n{Artist}\n{Album}"
    width, height = (canvas.winfo_width(), canvas.winfo_height())

    font = 20
    
    if size == 1:
        x = padding
        y = int(((height/2)+(padding*2)))
        twidth = width-(padding*2)        
    else:
        x:int = int((padding*2)+picturesize)
        y = int((height-picturesize)/2)
        twidth = int(width-(picturesize+(padding*2)))
    

    canvas.create_text(x, y, text=theText, width=twidth, fill="white", font=("Helvetica", font), anchor="nw")

def makemusic(canvas:tk.Canvas):

    size = getSize(canvas)

    picsize, _ = getMusicImg(canvas, size)


    metadata = get_latest_metadata()

    print(metadata.get("title"), metadata.get("artist"), metadata.get("album"))
    getTitle(canvas,size, picsize, metadata.get("title"), metadata.get("artist"), metadata.get("album"))

    canvas.config(bg="black")
    def updatemusic(metadata:dict[Any,Any]):
        new_metadata = get_latest_metadata()
        if new_metadata and new_metadata != metadata:
            canvas.delete("all")
            print(new_metadata.get("album"), new_metadata.get("artist"), new_metadata.get("title"))
            getMusicImg(canvas, size)
            getTitle(canvas,size, picsize, new_metadata.get("title"), new_metadata.get("artist"), new_metadata.get("album"))            

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