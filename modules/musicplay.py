import base64
import re
from PIL import Image
from io import BytesIO
from typing import Any

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


import tkinter as tk
from utilities.window import makeWindow
from utilities.makeWindows import makeCanvasDict
from layoutmaker.getLayout import getLayoutData

# Path to Shairport Sync metadata pipe
PIPE_PATH = "/tmp/shairport-sync-metadata"

song_title = None
artist = None
album = None
credits = None
genre = None
cover_art_image = None



# Make sure pipe exists
if not os.path.exists(PIPE_PATH):
    raise FileNotFoundError(f"{PIPE_PATH} does not exist. Make sure Shairport Sync is running with pipe_name.")

# Variables to store current metadata
song_title = None
artist = None
album = None
cover_art_image = None  # PIL Image object

# Map known Shairport Sync codes to friendly names
# You may need to adjust based on your version
code_map = {
    "6173616c": "album",
    "61736172": "artist",
    "61736370": "credits",   # optional, can be used separately
    "6173676e": "genre",     # optional
    "6d696e6d": "title",
    "6d706572": "cover_art"
}


def parse_metadata_block(block: str):
    """Parse a single <item>...</item> block and return (code, decoded data)."""
    code_match = re.search(r"<code>(.*?)</code>", block)
    data_match = re.search(r"<data.*?>(.*?)</data>", block, re.DOTALL)

    if not code_match or not data_match:
        return None, None

    code_val = code_match.group(1)
    data_val = data_match.group(1).strip()

    try:
        decoded_data = base64.b64decode(data_val)
    except Exception:
        decoded_data = data_val.encode()

    return code_val, decoded_data

def getmusicData() -> dict[str,Any]:

    buffer = ""

    with open(PIPE_PATH, "r") as pipe:  # text mode works better for XML
        print("Listening to Shairport Sync metadata...")
        while True:
            musicdata:dict[str,Any] = {}
            line = pipe.readline()
            if not line:
                continue
            buffer += line

            # Process complete <item> blocks
            while "</item>" in buffer:
                block, buffer = buffer.split("</item>", 1)
                block += "</item>"

                # DEBUG: Uncomment to see raw block
                # print("Raw block:", block)

                code_val, data = parse_metadata_block(block)
                if not code_val:
                    continue

                field = code_map.get(code_val)
                if not field:
                    continue

                if field == "cover_art":
                    try:
                        cover_art_image = Image.open(BytesIO(data)) #type:ignore
                        print("Cover art updated!")
                    except Exception:
                        cover_art_image = None
                    musicdata[field] = cover_art_image
                    
                else:
                    text = data.decode("utf-8", errors="ignore") #type:ignore
                    musicdata[field]= text

                    # Print current metadata
                    print(f"{field.capitalize()}: {text}")
                return musicdata

def drawSongCover(canvas: tk.Canvas, img:Any, padding:int =15):

    canvas.create_image(padding, padding, image=img, anchor="nw") #type:ignore
    canvas.image = img #type:ignore
    pass
    
def makemusic(canvas:tk.Canvas):
    musicData = getmusicData()
    drawSongCover(canvas, musicData["cover_art"])
    canvas.config(bg = "black")


def main() -> tk.Tk:
    root, dims = makeWindow(title="Weather")
    canvases = makeCanvasDict(root, getLayoutData(), dims)
    root.update_idletasks()
    makemusic(canvases["music"][0])

    return root

if __name__ == '__main__':
    root = main()
    root.mainloop()