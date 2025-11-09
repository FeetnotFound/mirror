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
from PIL import Image #type:ignore
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
    print(topic)
    if topic.endswith("cover"):
        print(topic)


    else:
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
mqtt_client = start_mqtt_listener()

def makemusic(canvas:tk.Canvas):
    metadata = get_latest_metadata()
    print(metadata["album"], metadata["artist"], metadata["title"])
    def updatemusic():
            metadata = get_latest_metadata()

            print(metadata["album"], metadata["artist"], metadata["title"])
            canvas.after(1000, updatemusic)

    updatemusic()


def main() -> tk.Tk:
    root, dims = makeWindow(title = "music")
    canvases = makeCanvasDict(root, getLayoutData(), dims)
    root.update_idletasks()
    makemusic(canvases["music"][0])

    return root


if __name__ == '__main__':
    root = main()

    root.mainloop()