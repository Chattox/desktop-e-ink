from datetime import datetime
import pytz

class Reading:
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
