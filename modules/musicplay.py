import socket
import os
from typing import Any

# -------------------
# Configuration
# -------------------
HOST = "127.0.0.1"   # Shairport Sync metadata socket address
PORT = 5555          # Shairport Sync metadata socket port
COVER_ART_FILE = "/tmp/current_cover.jpg"  # where cover art will be saved
# -------------------

def parse_metadata(data: bytes) -> dict[Any, Any]:
    """
    Parses metadata packets from Shairport Sync.
    Returns a dictionary with keys like Title, Artist, Album, CoverArt.
    """
    text = data.decode('utf-8', errors='ignore').replace('\x00', '')
    metadata:dict[Any, Any] = {}
    for line in text.split('\n'):
        if '=' in line:
            key, value = line.split('=', 1)
            metadata[key.strip()] = value.strip()
    return metadata

def save_cover_art(base64_data):
    """Save cover art (base64-encoded) to a file."""
    import base64
    try:
        img_data = base64.b64decode(base64_data)
        os.makedirs(os.path.dirname(COVER_ART_FILE), exist_ok=True)
        with open(COVER_ART_FILE, 'wb') as f:
            f.write(img_data)
        print(f"Cover art saved to {COVER_ART_FILE}")
    except Exception as e:
        print(f"Failed to save cover art: {e}")

def main():
    print("Connecting to Shairport Sync metadata socket...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Connected! Waiting for song metadata...\n")
        last_track = None

        while True:
            data = s.recv(65536)  # large enough for cover art
            if not data:
                break
            md = parse_metadata(data)
            # Only print when song changes
            track_id = (md.get('Title'), md.get('Artist'), md.get('Album'))
            if track_id != last_track and any(track_id):
                last_track = track_id
                print(f"Now Playing: {md.get('Title')} — {md.get('Artist')} ({md.get('Album')})")
            # Save cover art if present
            if 'CoverArt' in md:
                save_cover_art(md['CoverArt'])

if __name__ == "__main__":
    main()
