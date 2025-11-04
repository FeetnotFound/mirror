import yaml
from typing import Any, Union

output_file: str = "layout"
l_third= 1/3

small_land = [l_third, 0.25]
medium_land = [l_third, 0.3]
big_land = [l_third, 0.5]
clock_land: list[Union[int, float]] = [1, 0.2]


bg_color: str  = "black"
clock_bg_color: str  = "white"
calendar_bg_color: str  = "red"
event_bg_color: str  = "blue"
music_bg_color: str  = "green"
notifs_bg_color: str  = "yellow"
miller_bg_color: str  = "purple"
something_bg_color: str  = "pink"
status_bg_color:str  = "brown"




data: dict[str, Any]= {
    "orienttation": True,
    "layout": {
        "Hello": {
            "x":1,
            "y":2,
            "size": 1,
            "color":"black"
        },
        "Pooper": {
            "x":1,
            "y":2,
            "size": 2,
            "color":"black"
        }
    }
}



with open(f"{output_file}.yaml", 'w') as file:
    yaml.dump(data, file, default_flow_style=False, sort_keys=False)

print(f"Data succesfully written to '{output_file}'")