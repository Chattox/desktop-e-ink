import json
from datetime import datetime
import pytz

class Reading:
    """Handle and format reading data from API response"""
    def __init__(self, data):
        timestamp_obj = datetime.strptime(data[0]["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
        aware_ts_obj = pytz.timezone("UTC").localize(timestamp_obj)
        self.time_str = aware_ts_obj.astimezone(pytz.timezone("Europe/London")).strftime('%d/%m/%y %H:%M')
        self.temperature = data[0]["readings"]["temperature"]
        self.pressure = data[0]["readings"]["pressure"]
        self.humidity = data[0]["readings"]["humidity"]
        self.luminance = data[0]["readings"]["luminance"]
        self.rain = data[0]["readings"]["rain"]
        self.wind_speed = round(float(data[0]["readings"]["wind_speed"]), 2)
        compass_dirs = {
            0: "S",
            45: "SW",
            90: "W",
            135: "NW",
            180: "N",
            225: "NE",
            270: "E",
            315: "SE",
            360: "S",
        }
        self.wind_direction = compass_dirs[data[0]["readings"]["wind_direction"]]
        self.changes = { # These should always be either "inc", "dec", or "same"
            "temperature": "same",
            "pressure": "same",
            "humidity": "same",
            "luminance": "same",
            "rain": "same",
            "wind_speed": "same"
        }

    def get_changes_and_save(self):
        """Compare current reading to previous
        Update self.changes with increases and decreases
        Save reading to last_reading.json or create if doesn't exist
        """

        with open("last_reading.json", "r") as f_read:
            last_reading = json.load(f_read)
            self.changes = last_reading["changes"] # populate changes from file for consistency
            if last_reading["reading"]["time_str"] != self.time_str: # if no new reading, don't change anything
                for r in last_reading["reading"]:
                    if r != "time_str":
                        if getattr(self, r) > last_reading["reading"][r]:
                            self.changes[r] = "inc"
                        elif getattr(self, r) < last_reading["reading"][r]:
                            self.changes[r] = "dec"
                        else:
                            self.changes[r] = "same"
                with open("last_reading.json", "w") as f_write:
                    new_reading = {
                        "reading": {
                        "time_str": self.time_str,
                        "temperature": self.temperature,
                        "pressure": self.pressure,
                        "humidity": self.humidity,
                        "luminance": self.luminance,
                        "rain": self.rain,
                        "wind_speed": self.wind_speed
                        },
                        "changes": self.changes
                    }
                    json.dump(new_reading, f_write, ensure_ascii = False, indent = 4)
            print(self.changes)
        
        


