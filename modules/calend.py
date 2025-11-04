# https://forum.magicmirror.builders/topic/5327/sync-private-icloud-calendar-with-magicmirror/2?page=1
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any
from datetime import datetime, timedelta

import caldav
import pytz
# from time import sleep


from pathlib import Path
from dotenv import load_dotenv

# Step 1: Find the parent folder
parent_folder = Path(__file__).resolve().parent.parent

# Step 2: Specify the path to the .env file
env_path = parent_folder / "variables.env"

# Step 3: Load it
load_dotenv(dotenv_path=env_path)



import tkinter as tk
from utilities.window import makeWindow
from utilities.makeWindows import makeCanvasDict
from layoutmaker.getLayout import getLayoutData

APPLE_ID = os.getenv("ICLOUD_EMAIL")
APPLE_PASSWORD = os.getenv("CALENDAR_PASS")

CALENDAR_URL = 'https://caldav.icloud.com'
WANTEDCALS = ["Family"]#, "Cleaning"]
IGNORELIST = ["Trash out","Recycling out","Katzen Krallen","Switch pajamas","Katzen wasser"]

def to_local(dt:Any):
    """Convert a datetime or date to local timezone safely."""
    if not dt:
        return None

    if isinstance(dt, datetime):

        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)

        local_tz = pytz.timezone("America/Los_Angeles")
        return dt.astimezone(local_tz)
    return dt

def getClient() -> Any:
    return caldav.DAVClient(url=CALENDAR_URL, username=APPLE_ID, password=APPLE_PASSWORD) #type:ignore
    
def getCalendar(client:Any = getClient())-> list[Any]:
    principal = client.principal()
    return principal.calendars()
    
def getEventDetails(events:Any, calendar:str, calendarDict:dict[str, list[dict[str,Any]]]):
    for event in events:

        vevent = event.instance.vevent

        summary = getattr(vevent, "summary", None)
        location = getattr(vevent, "location", None)
        start = getattr(vevent, "dtstart", None)
        end = getattr(vevent, "dtend", None)


        start_local = to_local(start.value if start else None)
        end_local = to_local(end.value if end else None)

        summary = summary.value if summary else "—"
        location = location.value if location else "—"
        start = start_local.strftime("%d, %m, %H:%M") if start_local else "—"
        end = end_local.strftime("%d, %m, %H:%M") if end_local else "—"


        startDate = start_local.strftime("%m:%d") if start_local else "—"
        calendar = str(calendar)

        
        if summary in IGNORELIST:
            continue

        try: 
            calendarDict[startDate].append({"summary": summary, "location": location, "start": start, "end": end, "calendar": calendar})
        except: 
            calendarDict[startDate] = [{"summary": summary, "location": location, "start": start, "end": end, "calendar": calendar}]
    return calendarDict

def getCalendarEvents(wantedCals: list[str],timerange: int, calendDict:dict[str, list[dict[str,Any]]] = {}):
    calendDict = {}
    today = datetime.now()
    start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = (today + timedelta(days=timerange)).replace(hour=0, minute=0, second=0, microsecond=0)
    for cal in getCalendar():
        if str(cal) in wantedCals:
            events = cal.date_search(start=start_date, end=end_date)
            calendDict = getEventDetails(events, cal, calendDict)
    return calendDict

def monthday_to_weekday(date_str: str) -> str:
    """
    Convert a string in "MM:DD" format to "Weekday D",
    assuming the current year.
    """
    # Add current year
    current_year = datetime.now().year
    full_date_str = f"{current_year}:{date_str}"  # "YYYY:MM:DD"
    
    # Parse into a datetime object
    dt = datetime.strptime(full_date_str, "%Y:%m:%d")
    
    # Format as "Weekday day_of_month"
    try:
        return dt.strftime("%A %-d")  # Linux/macOS
    except ValueError:
        return dt.strftime("%A %#d") 

def create_rounded_rectangle(canvas:tk.Canvas, x1:int, y1:int, x2:int, y2:int, radii:tuple[int,int,int,int]=(20, 20, 20, 20), **kwargs): #type:ignore
    """
    Draw a rectangle with individually rounded corners without overlaps.
    radii = (top-left, top-right, bottom-right, bottom-left)
    """
    tl, tr, br, bl = radii

    max_width = (x2 - x1) / 2
    max_height = (y2 - y1) / 2
    tl = min(tl, max_width, max_height)
    tr = min(tr, max_width, max_height)
    br = min(br, max_width, max_height)
    bl = min(bl, max_width, max_height)

    # Center rectangle 
    canvas.create_rectangle(x1 + tl, y1 + tl, x2 - br, y2 - br, **kwargs) #type:ignore

    # Top rectangle
    canvas.create_rectangle(x1 + tl, y1, x2 - tr, y1 + max(tl, tr), **kwargs) #type:ignore
    # Bottom rectangle
    canvas.create_rectangle(x1 + bl, y2 - max(bl, br), x2 - br, y2, **kwargs) #type:ignore
    # Left rectangle
    canvas.create_rectangle(x1, y1 + tl, x1 + max(tl, bl), y2 - bl, **kwargs) #type:ignore
    # Right rectangle
    canvas.create_rectangle(x2 - max(tr, br), y1 + tr, x2, y2 - br, **kwargs) #type:ignore

    # Corner arcs
    canvas.create_arc(x1, y1, x1 + 2*tl, y1 + 2*tl, start=90, extent=90, style="pieslice", **kwargs) #type:ignore
    canvas.create_arc(x2 - 2*tr, y1, x2, y1 + 2*tr, start=0, extent=90, style="pieslice", **kwargs) #type:ignore
    canvas.create_arc(x2 - 2*br, y2 - 2*br, x2, y2, start=270, extent=90, style="pieslice", **kwargs) #type:ignore
    canvas.create_arc(x1, y2 - 2*bl, x1 + 2*bl, y2, start=180, extent=90, style="pieslice", **kwargs) #type:ignore

def drawCalendar(canvas:tk.Canvas, events: dict[str, list[dict[str, Any]]], padding:int = 5):

    calendar_colors:dict[str,str] = {
        "Family": "green",
        "Cleaning": "purple",
        "School": "red"
    }
    width = canvas.winfo_width()
    count = 0
    titleHeight = 50
    eventHeight = 100
    eventHeightTop = eventHeight*0.3
    for day, eventslist in events.items():#type:ignore
        day = monthday_to_weekday(day)

        x1 = int(((width/3)*count)+padding)
        x2 = int(((width/3)*(count+1))-padding)

        titleX = x1+((x2-x1)/2)

        titleY = (titleHeight+(padding*2))-(titleHeight/2)

        color = "red" if count==0 else "gray"

        create_rounded_rectangle(canvas, x1, padding*2, x2, titleHeight+(padding*2), radii=(20,20,10,10), fill=color, outline="", stipple = "gray12")  
        canvas.create_text(titleX, titleY, text=day, anchor="center", fill="white", font=("Helvetica", 24))
        for i, event in enumerate(eventslist, start=0):
            summary = event["summary"]
            location = event["location"].split("\n")[0]
            start = event["start"].split(", ")[-1]
            end = event["end"].split(", ")[-1]
            calendar = event["calendar"]

            
            y1 = (titleHeight+(padding*3))+((eventHeight+padding)*i)
            y2 = y1 + eventHeight


            if i == len(eventslist)-1:
                radius: tuple[int,int] = (20,20)
            else:
                radius: tuple[int,int] = (10,10)
            create_rounded_rectangle(canvas, x1, y1, x2, int(y1+eventHeightTop), radii=(10,10,0,0), fill = calendar_colors[calendar], outline = "", stipple = "gray75")  
            create_rounded_rectangle(canvas, x1, int(y1+eventHeightTop), x2, y2, radii=(0,0)+radius, fill = calendar_colors[calendar], outline = "", stipple = "gray25") 
            
            if start and end == "00:00":
                timeText = "All Day"
            else:
                timeText = f"{datetime.strptime(start, '%H:%M').strftime('%I:%M %p')} - {datetime.strptime(end, '%H:%M').strftime('%I:%M %p')}"
            canvas.create_text(x1+10, int(y1+(eventHeightTop/2)), text=timeText, fill = "white", anchor="w")

            

        
            y3 = int((y1+(eventHeightTop))+(eventHeight/10))
            y4 = int((y1+(eventHeightTop))+((eventHeight/10)*4))

            if location == "—":
                canvas.create_text(x1+10, y3, text=summary, width=(x2-x1)-10, fill = "white", anchor="nw", font=("Helvetica", 15))
            else:
                canvas.create_text(x1+10, y3, text=summary, width=(x2-x1)-10, fill = "white", anchor="nw", font=("Helvetica", 15))
                canvas.create_text(x1+10, y4, text=location, width=(x2-x1)-10, fill = "white", anchor="nw", font=("Helvetica", 12))
        count +=1

def makeCalendar(canvas:tk.Canvas, now_today:datetime, dateRange:int):
    events = getCalendarEvents(WANTEDCALS, timerange=dateRange)
    for eventlist in events.values():
        eventlist.sort(key=lambda x: datetime.strptime(x["start"], "%d, %m, %H:%M"))
    events = dict(
        sorted(
            events.items(),
            key=lambda x: datetime.strptime(x[0], "%m:%d")
        )
    )
    drawCalendar(canvas, events)
    return now_today

class calendar():

    size:list[int] = [3,4]

    def __init__(self, canvas: tk.Canvas) -> None:
        self.canvas = canvas
        self.today: datetime

    def displayCalendar(self, dateRange: int = 2):
        self.today = datetime.now()
        events = getCalendarEvents(WANTEDCALS, timerange=dateRange)

        for eventlist in events.values():
            eventlist.sort(key=lambda x: datetime.strptime(x["start"], "%d, %m, %H:%M"))
        
        events = dict(
            sorted(
                events.items(),
                key=lambda x: datetime.strptime(x[0], "%m:%d")
            )
        )


        drawCalendar(self.canvas, events)
        self.canvas.config(bg = "black")

        def update_calendar():
            now_today = datetime.now()
            if self.today.strftime("%m:%d:%Y") != now_today.strftime("%m:%d:%Y"):
                self.canvas.delete("all")

                self.today = makeCalendar(self.canvas, now_today, dateRange)

            self.canvas.after(1000, update_calendar)


        update_calendar()

def makecalendar(canvas:tk.Canvas):
    calendar(canvas).displayCalendar()

def main() -> tk.Tk:
    root, dims = makeWindow(title="Calendar")
    canvases = makeCanvasDict(root, getLayoutData(), dims)
    root.update_idletasks()
    makecalendar(canvases["calendar"][0])

    return root

if __name__ == '__main__':
    root = main()
    root.mainloop()
